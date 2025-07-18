import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# Configure Streamlit page
st.set_page_config(
    page_title="YouTube Content Automation Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

def make_api_request(endpoint, method="GET", data=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def main():
    st.title("🎬 YouTube Content Automation Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Overview", "Content Creation", "Analytics", "Trend Analysis", "Content Library"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Content Creation":
        show_content_creation()
    elif page == "Analytics":
        show_analytics()
    elif page == "Trend Analysis":
        show_trend_analysis()
    elif page == "Content Library":
        show_content_library()

def show_overview():
    """Show overview dashboard"""
    st.header("📊 Overview Dashboard")
    
    # Get dashboard data
    dashboard_data = make_api_request("/analytics/dashboard")
    
    if dashboard_data and dashboard_data.get("status") == "success":
        data = dashboard_data["data"]
        overview = data.get("overview", {})
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Videos",
                overview.get("total_videos", 0),
                delta="+5 this week"
            )
        
        with col2:
            st.metric(
                "Total Views",
                f"{overview.get('total_views', 0):,}",
                delta="+12.5%"
            )
        
        with col3:
            st.metric(
                "Avg Engagement Rate",
                f"{overview.get('avg_engagement_rate', 0):.1%}",
                delta="+2.3%"
            )
        
        with col4:
            st.metric(
                "Avg Retention Rate",
                f"{overview.get('avg_retention_rate', 0):.1%}",
                delta="+1.8%"
            )
        
        # Performance trends
        st.subheader("📈 Performance Trends")
        trends = data.get("performance_trends", {})
        
        if trends:
            col1, col2 = st.columns(2)
            
            with col1:
                # Views trend
                fig_views = go.Figure()
                fig_views.add_trace(go.Scatter(
                    x=list(range(1, len(trends.get("views_trend", [])) + 1)),
                    y=trends.get("views_trend", []),
                    mode='lines+markers',
                    name='Views',
                    line=dict(color='#1f77b4', width=3)
                ))
                fig_views.update_layout(
                    title="Views Trend",
                    xaxis_title="Weeks",
                    yaxis_title="Views",
                    height=300
                )
                st.plotly_chart(fig_views, use_container_width=True)
            
            with col2:
                # Engagement trend
                fig_engagement = go.Figure()
                fig_engagement.add_trace(go.Scatter(
                    x=list(range(1, len(trends.get("engagement_trend", [])) + 1)),
                    y=trends.get("engagement_trend", []),
                    mode='lines+markers',
                    name='Engagement Rate',
                    line=dict(color='#ff7f0e', width=3)
                ))
                fig_engagement.update_layout(
                    title="Engagement Rate Trend",
                    xaxis_title="Weeks",
                    yaxis_title="Engagement Rate",
                    height=300
                )
                st.plotly_chart(fig_engagement, use_container_width=True)
        
        # Recent performance
        st.subheader("🎯 Recent Video Performance")
        recent_videos = data.get("recent_performance", [])
        
        if recent_videos:
            df = pd.DataFrame(recent_videos)
            st.dataframe(df, use_container_width=True)
        
        # Insights
        st.subheader("💡 AI Insights")
        insights = data.get("insights", [])
        
        for insight in insights:
            st.info(f"💡 {insight}")
        
        # Content recommendations
        st.subheader("🎯 Content Recommendations")
        recommendations = data.get("content_recommendations", [])
        
        for rec in recommendations:
            with st.expander(f"📝 {rec.get('topic', 'Unknown Topic')} - {rec.get('priority', 'medium').title()} Priority"):
                st.write(f"**Estimated Views:** {rec.get('estimated_views', 0):,}")
                st.write(f"**Reason:** {rec.get('reason', 'No reason provided')}")
    
    else:
        st.error("Failed to load dashboard data. Please check if the API is running.")

def show_content_creation():
    """Show content creation interface"""
    st.header("🎬 Content Creation")
    
    # Content creation form
    with st.form("video_creation_form"):
        st.subheader("Create New Video")
        
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.selectbox(
                "Subject",
                ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History"]
            )
            grade = st.selectbox(
                "Grade",
                ["9", "10", "11", "12"]
            )
            topic = st.text_input("Topic", placeholder="e.g., Quadratic Equations")
        
        with col2:
            difficulty_level = st.selectbox(
                "Difficulty Level",
                ["easy", "medium", "hard"]
            )
            target_duration = st.slider(
                "Target Duration (minutes)",
                min_value=5,
                max_value=20,
                value=10
            )
            voice_style = st.selectbox(
                "Voice Style",
                ["professional", "friendly", "energetic"]
            )
        
        include_examples = st.checkbox("Include Examples", value=True)
        include_practice = st.checkbox("Include Practice Problems", value=True)
        
        submit_button = st.form_submit_button("🚀 Create Video")
        
        if submit_button:
            if not topic:
                st.error("Please enter a topic")
            else:
                # Create video request
                video_request = {
                    "subject": subject,
                    "grade": grade,
                    "topic": topic,
                    "difficulty_level": difficulty_level,
                    "target_duration": target_duration * 60,  # Convert to seconds
                    "include_examples": include_examples,
                    "include_practice": include_practice,
                    "voice_style": voice_style
                }
                
                # Make API request
                response = make_api_request("/create-video", method="POST", data=video_request)
                
                if response:
                    st.success(f"Video creation started! Job ID: {response.get('job_id')}")
                    st.info(f"Estimated completion time: {response.get('estimated_completion_time', 1800)} seconds")
                    
                    # Store job ID in session state for tracking
                    if 'job_ids' not in st.session_state:
                        st.session_state.job_ids = []
                    st.session_state.job_ids.append(response.get('job_id'))
    
    # Job status tracking
    st.subheader("📋 Job Status")
    
    if 'job_ids' in st.session_state and st.session_state.job_ids:
        for job_id in st.session_state.job_ids:
            with st.expander(f"Job: {job_id}"):
                # Get job status
                status_response = make_api_request(f"/video-status/{job_id}")
                
                if status_response:
                    status = status_response.get("status", "unknown")
                    progress = status_response.get("progress", 0)
                    message = status_response.get("message", "")
                    
                    # Status indicator
                    if status == "completed":
                        st.success(f"✅ Completed: {message}")
                        video_url = status_response.get("video_url")
                        if video_url:
                            st.write(f"**Video Path:** {video_url}")
                    elif status == "failed":
                        st.error(f"❌ Failed: {message}")
                    elif status == "processing":
                        st.info(f"🔄 Processing: {message}")
                        st.progress(progress / 100)
                    else:
                        st.warning(f"⏳ {status.title()}: {message}")
                
                # Refresh button
                if st.button(f"Refresh {job_id}", key=f"refresh_{job_id}"):
                    st.rerun()
    
    else:
        st.info("No active jobs. Create a video to see job status here.")

def show_analytics():
    """Show analytics dashboard"""
    st.header("📊 Analytics Dashboard")
    
    # Performance optimization section
    st.subheader("🎯 Performance Optimization")
    
    with st.form("optimization_form"):
        video_id = st.text_input("Video ID", placeholder="Enter video ID to optimize")
        
        st.write("**Target Metrics:**")
        col1, col2 = st.columns(2)
        
        with col1:
            target_views = st.number_input("Target Views", min_value=1000, value=50000)
            target_engagement = st.number_input("Target Engagement Rate", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
        
        with col2:
            target_retention = st.number_input("Target Retention Rate", min_value=0.1, max_value=1.0, value=0.7, step=0.01)
            target_ctr = st.number_input("Target Click-Through Rate", min_value=0.01, max_value=0.2, value=0.05, step=0.01)
        
        optimize_button = st.form_submit_button("🔍 Analyze & Optimize")
        
        if optimize_button and video_id:
            target_metrics = {
                "view_count": target_views,
                "engagement_rate": target_engagement,
                "retention_rate": target_retention,
                "click_through_rate": target_ctr
            }
            
            # Make optimization request
            response = make_api_request(f"/optimize-performance", method="POST", data={
                "video_id": video_id,
                "target_metrics": target_metrics
            })
            
            if response and response.get("status") == "success":
                optimization = response["optimization"]
                
                # Current vs Target metrics
                st.subheader("📈 Current vs Target Metrics")
                
                current_metrics = optimization.get("current_metrics", {})
                gaps = optimization.get("optimization_plan", {})
                
                metrics_df = pd.DataFrame([
                    {
                        "Metric": "Views",
                        "Current": current_metrics.get("view_count", 0),
                        "Target": target_views,
                        "Gap": gaps.get("view_count", {}).get("gap", 0)
                    },
                    {
                        "Metric": "Engagement Rate",
                        "Current": f"{current_metrics.get('engagement_rate', 0):.1%}",
                        "Target": f"{target_engagement:.1%}",
                        "Gap": f"{gaps.get('engagement_rate', {}).get('gap', 0):.1%}"
                    },
                    {
                        "Metric": "Retention Rate",
                        "Current": f"{current_metrics.get('retention_rate', 0):.1%}",
                        "Target": f"{target_retention:.1%}",
                        "Gap": f"{gaps.get('retention_rate', {}).get('gap', 0):.1%}"
                    }
                ])
                
                st.dataframe(metrics_df, use_container_width=True)
                
                # Recommendations
                st.subheader("💡 Optimization Recommendations")
                recommendations = optimization.get("recommendations", [])
                
                for rec in recommendations:
                    priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    priority_icon = priority_color.get(rec.get("priority", "medium"), "🟡")
                    
                    with st.expander(f"{priority_icon} {rec.get('title', 'Recommendation')}"):
                        st.write(f"**Priority:** {rec.get('priority', 'medium').title()}")
                        st.write(f"**Description:** {rec.get('description', 'No description')}")
                        st.write(f"**Estimated Impact:** {rec.get('estimated_impact', 'Unknown')}")
                
                # A/B Tests
                ab_tests = optimization.get("ab_tests", [])
                if ab_tests:
                    st.subheader("🧪 Suggested A/B Tests")
                    
                    for test in ab_tests:
                        with st.expander(f"Test: {test.get('test_type', 'Unknown').title()}"):
                            st.write(f"**Duration:** {test.get('duration_days', 0)} days")
                            st.write(f"**Success Metric:** {test.get('success_metric', 'Unknown')}")
                            
                            variants = test.get("variants", [])
                            for variant in variants:
                                st.write(f"- **{variant.get('name', 'Unknown')}:** {variant.get('description', 'No description')}")

def show_trend_analysis():
    """Show trend analysis"""
    st.header("📈 Trend Analysis")
    
    # Trend analysis form
    with st.form("trend_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.selectbox(
                "Subject",
                ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History"],
                key="trend_subject"
            )
        
        with col2:
            grade = st.selectbox(
                "Grade",
                ["9", "10", "11", "12"],
                key="trend_grade"
            )
        
        analyze_button = st.form_submit_button("🔍 Analyze Trends")
        
        if analyze_button:
            # Make trend analysis request
            response = make_api_request(f"/analyze-trends", method="POST", data={
                "subject": subject,
                "grade": grade
            })
            
            if response and response.get("status") == "success":
                analysis = response["analysis"]
                
                # Trending keywords
                st.subheader("🔥 Trending Keywords")
                keywords = analysis.get("trending_keywords", [])
                
                if keywords:
                    # Create keyword cloud visualization
                    keyword_data = []
                    for i, keyword in enumerate(keywords):
                        keyword_data.append({
                            "keyword": keyword,
                            "rank": i + 1,
                            "search_volume": analysis.get("search_volume_data", {}).get(keyword, 0)
                        })
                    
                    df = pd.DataFrame(keyword_data)
                    
                    # Bar chart of search volumes
                    fig = px.bar(
                        df,
                        x="keyword",
                        y="search_volume",
                        title="Search Volume by Keyword",
                        color="search_volume",
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Content opportunities
                st.subheader("🎯 Content Opportunities")
                opportunities = analysis.get("content_opportunities", [])
                
                for opp in opportunities:
                    with st.expander(f"📝 {opp.get('title', 'Opportunity')}"):
                        st.write(f"**Description:** {opp.get('description', 'No description')}")
                        st.write(f"**Estimated Views:** {opp.get('estimated_views', 0):,}")
                        st.write(f"**Priority Score:** {opp.get('priority_score', 0):.2f}")
                        st.write(f"**Target Audience:** {opp.get('target_audience', 'Unknown')}")
                        
                        key_concepts = opp.get("key_concepts", [])
                        if key_concepts:
                            st.write(f"**Key Concepts:** {', '.join(key_concepts)}")
                
                # Market insights
                st.subheader("📊 Market Insights")
                insights = analysis.get("market_insights", {})
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Competition Level",
                        insights.get("level", "medium").title()
                    )
                
                with col2:
                    st.metric(
                        "Average Views",
                        f"{insights.get('avg_views', 0):,.0f}"
                    )
                
                with col3:
                    st.metric(
                        "Videos Analyzed",
                        insights.get("total_videos_analyzed", 0)
                    )
    
    # Content idea generation
    st.subheader("💡 Generate Content Ideas")
    
    with st.form("content_ideas_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            idea_subject = st.selectbox(
                "Subject",
                ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History"],
                key="idea_subject"
            )
            idea_grade = st.selectbox(
                "Grade",
                ["9", "10", "11", "12"],
                key="idea_grade"
            )
        
        with col2:
            idea_topic = st.text_input("Topic", placeholder="e.g., Quadratic Equations")
            idea_difficulty = st.selectbox(
                "Difficulty Level",
                ["easy", "medium", "hard"],
                key="idea_difficulty"
            )
        
        generate_button = st.form_submit_button("🎯 Generate Ideas")
        
        if generate_button and idea_topic:
            # Make content ideas request
            response = make_api_request(f"/generate-content-ideas", method="POST", data={
                "subject": idea_subject,
                "grade": idea_grade,
                "topic": idea_topic,
                "difficulty_level": idea_difficulty
            })
            
            if response and response.get("status") == "success":
                ideas = response["ideas"]
                
                st.subheader("🎬 Generated Content Ideas")
                
                for idea in ideas:
                    with st.expander(f"📝 {idea.get('title', 'Idea')}"):
                        st.write(f"**Description:** {idea.get('description', 'No description')}")
                        st.write(f"**Estimated Views:** {idea.get('estimated_views', 0):,}")
                        st.write(f"**Priority Score:** {idea.get('priority_score', 0):.2f}")
                        st.write(f"**Production Time:** {idea.get('estimated_production_time', 0)} minutes")
                        
                        key_concepts = idea.get("key_concepts", [])
                        if key_concepts:
                            st.write(f"**Key Concepts:** {', '.join(key_concepts)}")

def show_content_library():
    """Show content library"""
    st.header("📚 Content Library")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_subject = st.selectbox(
            "Filter by Subject",
            ["All", "Mathematics", "Physics", "Chemistry", "Biology", "English", "History"]
        )
    
    with col2:
        filter_grade = st.selectbox(
            "Filter by Grade",
            ["All", "9", "10", "11", "12"]
        )
    
    with col3:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All", "pending", "processing", "completed", "failed"]
        )
    
    # Get content library
    params = {}
    if filter_subject != "All":
        params["subject"] = filter_subject
    if filter_grade != "All":
        params["grade"] = filter_grade
    if filter_status != "All":
        params["status"] = filter_status
    
    # Build query string
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    endpoint = f"/content-library"
    if query_string:
        endpoint += f"?{query_string}"
    
    response = make_api_request(endpoint)
    
    if response and response.get("status") == "success":
        content = response["content"]
        
        if content:
            st.subheader(f"📋 Content Library ({len(content)} items)")
            
            # Convert to DataFrame for better display
            df_data = []
            for item in content:
                df_data.append({
                    "Title": item.get("title", "Unknown"),
                    "Subject": item.get("subject", "Unknown"),
                    "Grade": item.get("grade", "Unknown"),
                    "Topic": item.get("topic", "Unknown"),
                    "Status": item.get("status", "Unknown"),
                    "Quality Score": f"{item.get('quality_score', 0):.2f}" if item.get('quality_score') else "N/A",
                    "Views": f"{item.get('view_count', 0):,}" if item.get('view_count') else "N/A",
                    "Created": item.get("created_at", "Unknown")
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Content", len(content))
            
            with col2:
                completed_count = len([c for c in content if c.get("status") == "completed"])
                st.metric("Completed", completed_count)
            
            with col3:
                avg_quality = sum([c.get("quality_score", 0) for c in content if c.get("quality_score")]) / max(len([c for c in content if c.get("quality_score")]), 1)
                st.metric("Avg Quality", f"{avg_quality:.2f}")
            
            with col4:
                total_views = sum([c.get("view_count", 0) for c in content if c.get("view_count")])
                st.metric("Total Views", f"{total_views:,}")
        
        else:
            st.info("No content found matching the selected filters.")
    
    else:
        st.error("Failed to load content library.")

if __name__ == "__main__":
    main()