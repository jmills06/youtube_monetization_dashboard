#!/usr/bin/env python3
"""
YouTube Monetization Data Fetcher for The Everyday Ham Podcast
Fetches revenue metrics and stores them in JSON format for dashboard display
"""

from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import pickle
import os

# OAuth scopes - includes monetary scope for revenue data
SCOPES = [
    'https://www.googleapis.com/auth/youtube.readonly',
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/yt-analytics-monetary.readonly'
]

def authenticate():
    """
    Authenticate with YouTube Analytics API using token.pickle
    """
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        raise Exception("Invalid or missing credentials. Please regenerate token.pickle")
    
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
    return youtube_analytics

def fetch_revenue_metrics(youtube_analytics, start_date, end_date):
    """
    Fetch core revenue metrics for the specified date range
    """
    try:
        response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=end_date.strftime('%Y-%m-%d'),
            metrics='estimatedRevenue,cpm,monetizedPlaybacks,adImpressions',
            currency='USD'
        ).execute()
        
        return response
    except Exception as e:
        print(f"Error fetching revenue metrics: {e}")
        return None

def fetch_daily_revenue(youtube_analytics, start_date, end_date):
    """
    Fetch daily revenue data for trend chart
    """
    try:
        response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=end_date.strftime('%Y-%m-%d'),
            metrics='estimatedRevenue',
            dimensions='day',
            sort='day',
            currency='USD'
        ).execute()
        
        return response
    except Exception as e:
        print(f"Error fetching daily revenue: {e}")
        return None

def fetch_revenue_by_ad_type(youtube_analytics, start_date, end_date):
    """
    Fetch revenue breakdown by ad type
    """
    try:
        response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=end_date.strftime('%Y-%m-%d'),
            metrics='estimatedRevenue',
            dimensions='adType',
            sort='-estimatedRevenue',
            currency='USD'
        ).execute()
        
        return response
    except Exception as e:
        print(f"Error fetching ad type revenue: {e}")
        return None

def fetch_top_earning_videos(youtube_analytics, start_date, end_date):
    """
    Fetch top earning videos for the period
    """
    try:
        response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=end_date.strftime('%Y-%m-%d'),
            metrics='estimatedRevenue,views',
            dimensions='video',
            sort='-estimatedRevenue',
            maxResults=5,
            currency='USD'
        ).execute()
        
        return response
    except Exception as e:
        print(f"Error fetching top earning videos: {e}")
        return None

def fetch_video_titles(youtube_analytics, video_ids):
    """
    Fetch video titles for the given video IDs using YouTube Data API
    """
    try:
        # Build YouTube Data API client
        from googleapiclient.discovery import build
        youtube_data = build('youtube', 'v3', credentials=youtube_analytics._http.credentials)
        
        response = youtube_data.videos().list(
            part='snippet',
            id=','.join(video_ids)
        ).execute()
        
        titles = {}
        for item in response.get('items', []):
            titles[item['id']] = item['snippet']['title']
        
        return titles
    except Exception as e:
        print(f"Error fetching video titles: {e}")
        return {}

def fetch_total_views(youtube_analytics, start_date, end_date):
    """
    Fetch total views for RPM calculation
    """
    try:
        response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date.strftime('%Y-%m-%d'),
            endDate=end_date.strftime('%Y-%m-%d'),
            metrics='views'
        ).execute()
        
        return response
    except Exception as e:
        print(f"Error fetching total views: {e}")
        return None

def calculate_rpm(revenue, views):
    """
    Calculate RPM (Revenue Per Mille/1000 views)
    """
    if views and views > 0:
        return (revenue / views) * 1000
    return 0

def calculate_percentage_change(current, previous):
    """
    Calculate percentage change between two values
    """
    if previous and previous > 0:
        return ((current - previous) / previous) * 100
    return 0

def fetch_previous_period_metrics(youtube_analytics, start_date, end_date):
    """
    Fetch metrics from the previous 30-day period for comparison
    """
    period_length = (end_date - start_date).days
    prev_end = start_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_length)
    
    try:
        response = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=prev_start.strftime('%Y-%m-%d'),
            endDate=prev_end.strftime('%Y-%m-%d'),
            metrics='estimatedRevenue,cpm,monetizedPlaybacks,views',
            currency='USD'
        ).execute()
        
        return response
    except Exception as e:
        print(f"Error fetching previous period metrics: {e}")
        return None

def main():
    """
    Main execution function
    """
    print("Starting YouTube Monetization data fetch...")
    
    # Authenticate
    youtube_analytics = authenticate()
    print("Authentication successful")
    
    # Calculate date range (last 30 days)
    end_date = datetime.now() - timedelta(days=1)  # Yesterday (API data lag)
    start_date = end_date - timedelta(days=29)  # 30 days total
    
    print(f"Fetching data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    # Initialize data structure
    data = {
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
        'period_start': start_date.strftime('%Y-%m-%d'),
        'period_end': end_date.strftime('%Y-%m-%d'),
    }
    
    # Fetch core revenue metrics
    print("Fetching core revenue metrics...")
    revenue_metrics = fetch_revenue_metrics(youtube_analytics, start_date, end_date)
    
    if revenue_metrics and 'rows' in revenue_metrics and len(revenue_metrics['rows']) > 0:
        row = revenue_metrics['rows'][0]
        total_revenue = row[0] if row[0] is not None else 0
        cpm = row[1] if row[1] is not None else 0
        monetized_playbacks = row[2] if row[2] is not None else 0
        ad_impressions = row[3] if row[3] is not None else 0
        
        data['total_revenue'] = round(total_revenue, 2)
        data['cpm'] = round(cpm, 2)
        data['monetized_playbacks'] = monetized_playbacks
        data['ad_impressions'] = ad_impressions
    else:
        print("Warning: No revenue data available")
        data['total_revenue'] = 0
        data['cpm'] = 0
        data['monetized_playbacks'] = 0
        data['ad_impressions'] = 0
    
    # Fetch total views for RPM calculation
    print("Fetching total views...")
    views_response = fetch_total_views(youtube_analytics, start_date, end_date)
    total_views = 0
    
    if views_response and 'rows' in views_response and len(views_response['rows']) > 0:
        total_views = views_response['rows'][0][0]
        data['total_views'] = total_views
    else:
        data['total_views'] = 0
    
    # Calculate RPM
    data['rpm'] = round(calculate_rpm(data['total_revenue'], total_views), 2)
    
    # Fetch previous period for comparison
    print("Fetching previous period metrics...")
    prev_metrics = fetch_previous_period_metrics(youtube_analytics, start_date, end_date)
    
    if prev_metrics and 'rows' in prev_metrics and len(prev_metrics['rows']) > 0:
        prev_row = prev_metrics['rows'][0]
        prev_revenue = prev_row[0] if prev_row[0] is not None else 0
        prev_cpm = prev_row[1] if prev_row[1] is not None else 0
        prev_playbacks = prev_row[2] if prev_row[2] is not None else 0
        prev_views = prev_row[3] if prev_row[3] is not None else 0
        
        prev_rpm = calculate_rpm(prev_revenue, prev_views)
        
        data['revenue_change'] = round(calculate_percentage_change(data['total_revenue'], prev_revenue), 1)
        data['rpm_change'] = round(calculate_percentage_change(data['rpm'], prev_rpm), 1)
        data['cpm_change'] = round(calculate_percentage_change(data['cpm'], prev_cpm), 1)
        data['playbacks_change'] = round(calculate_percentage_change(data['monetized_playbacks'], prev_playbacks), 1)
    else:
        data['revenue_change'] = 0
        data['rpm_change'] = 0
        data['cpm_change'] = 0
        data['playbacks_change'] = 0
    
    # Fetch daily revenue for trend chart
    print("Fetching daily revenue data...")
    daily_revenue = fetch_daily_revenue(youtube_analytics, start_date, end_date)
    
    revenue_chart = {
        'labels': [],
        'values': []
    }
    
    if daily_revenue and 'rows' in daily_revenue:
        for row in daily_revenue['rows']:
            date_str = row[0]  # Format: YYYY-MM-DD
            revenue = row[1] if row[1] is not None else 0
            
            # Format date as "Oct 01"
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%b %d')
            
            revenue_chart['labels'].append(formatted_date)
            revenue_chart['values'].append(round(revenue, 2))
    
    data['revenue_chart'] = revenue_chart
    
    # Fetch revenue by ad type
    print("Fetching revenue by ad type...")
    ad_type_revenue = fetch_revenue_by_ad_type(youtube_analytics, start_date, end_date)
    
    ad_type_breakdown = {}
    total_ad_revenue = 0
    
    if ad_type_revenue and 'rows' in ad_type_revenue:
        for row in ad_type_revenue['rows']:
            ad_type = row[0]
            revenue = row[1] if row[1] is not None else 0
            total_ad_revenue += revenue
        
        # Calculate percentages
        for row in ad_type_revenue['rows']:
            ad_type = row[0]
            revenue = row[1] if row[1] is not None else 0
            
            # Clean up ad type names
            ad_type_name = ad_type.replace('_', ' ').title()
            
            if total_ad_revenue > 0:
                percentage = (revenue / total_ad_revenue) * 100
                ad_type_breakdown[ad_type_name] = {
                    'percentage': round(percentage, 1),
                    'revenue': round(revenue, 2)
                }
    
    data['ad_type_breakdown'] = ad_type_breakdown
    
    # Fetch top earning videos
    print("Fetching top earning videos...")
    top_videos = fetch_top_earning_videos(youtube_analytics, start_date, end_date)
    
    top_earning_videos = []
    
    if top_videos and 'rows' in top_videos:
        # Extract video IDs
        video_ids = [row[0] for row in top_videos['rows']]
        
        # Fetch video titles
        video_titles = fetch_video_titles(youtube_analytics, video_ids)
        
        for row in top_videos['rows']:
            video_id = row[0]
            revenue = row[1] if row[1] is not None else 0
            views = row[2] if row[2] is not None else 0
            
            video_title = video_titles.get(video_id, f"Video {video_id}")
            
            top_earning_videos.append({
                'title': video_title,
                'revenue': round(revenue, 2),
                'views': views,
                'video_id': video_id
            })
    
    data['top_earning_videos'] = top_earning_videos
    
    # Calculate projected monthly earnings (based on current 30-day pace)
    if data['total_revenue'] > 0:
        # Average daily revenue
        days_in_period = (end_date - start_date).days + 1
        avg_daily_revenue = data['total_revenue'] / days_in_period
        
        # Project for a 30-day month
        data['projected_monthly_revenue'] = round(avg_daily_revenue * 30, 2)
    else:
        data['projected_monthly_revenue'] = 0
    
    # Save to JSON file
    output_file = 'youtube_monetization.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✅ Data successfully saved to {output_file}")
    print(f"Total Revenue: ${data['total_revenue']}")
    print(f"RPM: ${data['rpm']}")
    print(f"CPM: ${data['cpm']}")
    print(f"Monetized Playbacks: {data['monetized_playbacks']:,}")
    print(f"Ad Impressions: {data['ad_impressions']:,}")
    print(f"Top Earning Video: {top_earning_videos[0]['title'] if top_earning_videos else 'N/A'}")

if __name__ == '__main__':
    main()
