import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re

# Set up the page
st.set_page_config(
    page_title="Voicestack Dental Call Analytics",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Voicestack - Dental Front Desk Call Dashboard")
#st.markdown("**AI Classification**")

# File upload section
st.subheader("📁 Upload Call Data")
uploaded_file = st.file_uploader("Choose your CSV file", type=['csv'])

# REAL AI CLASSIFICATION FUNCTIONS
def classify_call_purpose(transcript):
    """Real AI classification based on transcript content"""
    if pd.isna(transcript) or transcript == "":
        return "Unknown"
    
    transcript_lower = str(transcript).lower()
    
    # Booking detection
    booking_terms = ['schedule', 'appointment', 'booking', 'make an appt', 'book', 'reserve']
    if any(term in transcript_lower for term in booking_terms):
        return "Appointment Booking"
    
    # Cancellation detection
    cancel_terms = ['cancel', 'cancellation', 'reschedule', 'change appointment', 'can\'t make it']
    if any(term in transcript_lower for term in cancel_terms):
        return "Cancellation"
    
    # No-show detection
    noshow_terms = ['missed appointment', 'no show', 'didn\'t come', 'wasn\'t there', 'missed my appt']
    if any(term in transcript_lower for term in noshow_terms):
        return "No-Show Followup"
    
    # Billing detection
    billing_terms = ['bill', 'payment', 'insurance', 'cost', 'price', 'charge', 'fee']
    if any(term in transcript_lower for term in billing_terms):
        return "Billing/Insurance"
    
    # Emergency detection
    emergency_terms = ['emergency', 'hurt', 'pain', 'toothache', 'broken', 'urgent', 'swelling']
    if any(term in transcript_lower for term in emergency_terms):
        return "Clinical Emergency"
    
    return "General Inquiry"

def detect_booking_success(transcript):
    """Detect if booking attempt was successful"""
    if pd.isna(transcript) or transcript == "":
        return "Unknown"
    
    transcript_lower = str(transcript).lower()
    
    success_terms = ['sure', 'ok', 'great', 'confirmed', 'thank you', 'see you', 'scheduled', 'perfect', 'thanks']
    failure_terms = ['think about', 'call back', 'check', 'maybe', 'not sure', 'let me know', 'get back']
    
    success_count = sum(1 for term in success_terms if term in transcript_lower)
    failure_count = sum(1 for term in failure_terms if term in transcript_lower)
    
    if success_count > failure_count:
        return "Successful"
    elif failure_count > success_count:
        return "Failed"
    else:
        return "Unknown"

def analyze_sentiment(transcript):
    """Basic sentiment analysis from transcript"""
    if pd.isna(transcript) or transcript == "":
        return "Neutral"
    
    transcript_lower = str(transcript).lower()
    
    positive_terms = ['thank', 'thanks', 'appreciate', 'great', 'good', 'helpful', 'wonderful', 'excellent', 'perfect', 'happy']
    negative_terms = ['angry', 'frustrated', 'upset', 'disappointed', 'not happy', 'problem', 'issue', 'complaint', 'bad', 'terrible']
    
    positive_count = sum(1 for term in positive_terms if term in transcript_lower)
    negative_count = sum(1 for term in negative_terms if term in transcript_lower)
    
    if positive_count > negative_count:
        return "Positive"
    elif negative_count > positive_count:
        return "Negative"
    else:
        return "Neutral"

def detect_emotions(transcript):
    """Detect specific emotions in transcript"""
    if pd.isna(transcript) or transcript == "":
        return []
    
    transcript_lower = str(transcript).lower()
    emotions = []
    
    emotion_patterns = {
        'grateful': ['thank', 'appreciate', 'grateful'],
        'frustrated': ['frustrated', 'annoyed', 'angry', 'mad'],
        'anxious': ['worried', 'anxious', 'nervous', 'scared'],
        'satisfied': ['happy', 'satisfied', 'pleased', 'good'],
        'confused': ['confused', 'not sure', 'don\'t understand']
    }
    
    for emotion, terms in emotion_patterns.items():
        if any(term in transcript_lower for term in terms):
            emotions.append(emotion)
    
    return emotions[:3]  # Return top 3 emotions

def assess_call_quality(transcript, sentiment):
    """Assess call quality based on transcript and sentiment"""
    if pd.isna(transcript) or transcript == "":
        return "Unknown"
    
    transcript_lower = str(transcript).lower()
    words = len(transcript_lower.split())
    
    # Quality assessment logic
    if sentiment == 'Positive' and words > 30:
        return "Excellent"
    elif sentiment == 'Positive':
        return "Good"
    elif sentiment == 'Negative' and words < 10:
        return "Poor"
    elif sentiment == 'Negative':
        return "Needs Improvement"
    else:
        return "Average"

if uploaded_file is not None:
    # Load data
    data = pd.read_csv(uploaded_file)
    
    # Basic data cleaning
    date_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
    for date_col in date_columns:
        data[date_col] = pd.to_datetime(data[date_col], errors='coerce')
    
    st.success(f"✅ Successfully loaded {len(data)} calls")
    
    # APPLY REAL AI CLASSIFICATION
    if 'transcript' in data.columns:
        with st.spinner("🤖 Applying AI classification to call transcripts..."):
            data['Call_Purpose'] = data['transcript'].apply(classify_call_purpose)
            data['Booking_Success'] = data['transcript'].apply(detect_booking_success)
            data['Sentiment'] = data['transcript'].apply(analyze_sentiment)
            data['Emotions'] = data['transcript'].apply(detect_emotions)
            data['Call_Quality'] = data.apply(lambda row: assess_call_quality(row['transcript'], row['Sentiment']), axis=1)
        st.success("✅ AI classification completed!")
    
    # =================================================================
    # 1. QUANTITATIVE METRICS DASHBOARD WITH CHARTS
    # =================================================================
    
    st.header("📊 QUANTITATIVE METRICS")
    
    # 1. CALL VOLUMES DASHBOARD
    st.subheader("📞 1. Call Volumes Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Call Direction Pie Chart
        direction_cols = [col for col in data.columns if 'direction' in col.lower()]
        if direction_cols:
            direction_counts = data[direction_cols[0]].value_counts()
            fig = px.pie(
                values=direction_counts.values,
                names=direction_counts.index,
                title="Call Direction Distribution",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Call direction data not available")
    
    with col2:
        # Call Status Pie Chart
        status_cols = [col for col in data.columns if 'status' in col.lower()]
        if status_cols:
            status_counts = data[status_cols[0]].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Call Status Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Call status data not available")
    
    # Call Volume Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_calls = len(data)
        st.metric("Total Calls", total_calls)
    
    with col2:
        if direction_cols:
            inbound_calls = data[data[direction_cols[0]] == 'Inbound'].shape[0]
            st.metric("Inbound Calls", inbound_calls)
        else:
            st.metric("Inbound Calls", "N/A")
    
    with col3:
        if status_cols:
            answered_calls = data[data[status_cols[0]] == 'Answered'].shape[0]
            st.metric("Answered Calls", answered_calls)
        else:
            st.metric("Answered Calls", "N/A")
    
    with col4:
        if status_cols:
            missed_calls = data[data[status_cols[0]] == 'Missed'].shape[0]
            st.metric("Missed Calls", missed_calls)
        else:
            st.metric("Missed Calls", "N/A")
    
    with col5:
        contact_cols = [col for col in data.columns if 'contact' in col.lower()]
        if contact_cols:
            new_patients = data[data[contact_cols[0]] == 'New Patient'].shape[0]
            st.metric("New Patient Calls", new_patients)
        else:
            st.metric("New Patients", "N/A")
    
    # 2. BOOKING CONVERSION RATES DASHBOARD
    st.subheader("🎯 2. Booking Conversion Rates")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Call_Purpose' in data.columns:
            # Booking Purpose Distribution
            purpose_counts = data['Call_Purpose'].value_counts()
            fig = px.pie(
                values=purpose_counts.values,
                names=purpose_counts.index,
                title="Call Purpose Distribution (AI Classified)",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Call purpose analysis requires transcript data")
    
    with col2:
        if 'Call_Purpose' in data.columns and 'Booking_Success' in data.columns:
            # Booking Success Pie Chart
            booking_data = data[data['Call_Purpose'] == 'Appointment Booking']
            if len(booking_data) > 0:
                success_counts = booking_data['Booking_Success'].value_counts()
                fig = px.pie(
                    values=success_counts.values,
                    names=success_counts.index,
                    title="Booking Success Rate (AI Analyzed)",
                    color=success_counts.index,
                    color_discrete_map={'Successful': 'green', 'Failed': 'red', 'Unknown': 'gray'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No booking calls detected in transcripts")
        else:
            st.info("Booking success analysis requires transcript data")
    
    # Booking Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if 'Call_Purpose' in data.columns:
            booking_calls = data[data['Call_Purpose'] == 'Appointment Booking'].shape[0]
            st.metric("Booking Inquiries", booking_calls)
        else:
            st.metric("Booking Inquiries", "No transcript data")
    
    with col2:
        if 'Call_Purpose' in data.columns and 'Booking_Success' in data.columns:
            successful_bookings = data[
                (data['Call_Purpose'] == 'Appointment Booking') & 
                (data['Booking_Success'] == 'Successful')
            ].shape[0]
            st.metric("Successful Bookings", successful_bookings)
        else:
            st.metric("Successful Bookings", "No transcript data")
    
    with col3:
        if 'Call_Purpose' in data.columns and 'Booking_Success' in data.columns:
            booking_calls = data[data['Call_Purpose'] == 'Appointment Booking'].shape[0]
            successful_bookings = data[
                (data['Call_Purpose'] == 'Appointment Booking') & 
                (data['Booking_Success'] == 'Successful')
            ].shape[0]
            conversion_rate = (successful_bookings / booking_calls * 100) if booking_calls > 0 else 0
            st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        else:
            st.metric("Conversion Rate", "No transcript data")
    
    with col4:
        if 'Call_Purpose' in data.columns and 'Booking_Success' in data.columns:
            failed_bookings = data[
                (data['Call_Purpose'] == 'Appointment Booking') & 
                (data['Booking_Success'] == 'Failed')
            ].shape[0]
            st.metric("Failed Bookings", failed_bookings)
        else:
            st.metric("Failed Bookings", "No transcript data")
    
    with col5:
        if 'Call_Purpose' in data.columns:
            total_bookings = data[data['Call_Purpose'] == 'Appointment Booking'].shape[0]
            total_calls = len(data)
            booking_rate = (total_bookings / total_calls * 100) if total_calls > 0 else 0
            st.metric("Booking Call Rate", f"{booking_rate:.1f}%")
        else:
            st.metric("Booking Call Rate", "No transcript data")
    
    # 3. CANCELLATIONS DASHBOARD
    st.subheader("❌ 3. Cancellations Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Call_Purpose' in data.columns:
            # Cancellation vs Other Calls
            cancellation_data = data[data['Call_Purpose'] == 'Cancellation']
            other_calls = len(data) - len(cancellation_data)
            
            fig = px.pie(
                values=[len(cancellation_data), other_calls],
                names=['Cancellation Calls', 'Other Calls'],
                title="Cancellation Calls vs All Other Calls",
                color_discrete_sequence=['red', 'lightblue']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cancellation analysis requires transcript data")
    
    with col2:
        if 'Call_Purpose' in data.columns:
            # Cancellation Reason Analysis (Simple)
            cancellation_reasons = {
                'Reschedule': data['transcript'].str.contains('reschedule', na=False, case=False).sum(),
                'Emergency': data['transcript'].str.contains('emergency|can\'t make', na=False, case=False).sum(),
                'Other': data[data['Call_Purpose'] == 'Cancellation'].shape[0] - data['transcript'].str.contains('reschedule|emergency|can\'t make', na=False, case=False).sum()
            }
            
            fig = px.pie(
                values=list(cancellation_reasons.values()),
                names=list(cancellation_reasons.keys()),
                title="Cancellation Reasons (AI Detected)",
                color_discrete_sequence=px.colors.sequential.Reds
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cancellation reasons require transcript data")
    
    # Cancellation Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if 'Call_Purpose' in data.columns:
            cancellation_calls = data[data['Call_Purpose'] == 'Cancellation'].shape[0]
            st.metric("Cancellation Calls", cancellation_calls)
        else:
            st.metric("Cancellation Calls", "No transcript data")
    
    with col2:
        if 'Call_Purpose' in data.columns:
            total_calls = len(data)
            cancellation_rate = (cancellation_calls / total_calls * 100) if total_calls > 0 else 0
            st.metric("Cancellation Rate", f"{cancellation_rate:.1f}%")
        else:
            st.metric("Cancellation Rate", "No transcript data")
    
    with col3:
        if 'Call_Purpose' in data.columns:
            reschedule_calls = data['transcript'].str.contains('reschedule', na=False, case=False).sum()
            st.metric("Reschedule Requests", reschedule_calls)
        else:
            st.metric("Reschedule Requests", "No transcript data")
    
    with col4:
        if 'Call_Purpose' in data.columns:
            emergency_cancellations = data['transcript'].str.contains('emergency', na=False, case=False).sum()
            st.metric("Emergency Cancels", emergency_cancellations)
        else:
            st.metric("Emergency Cancels", "No transcript data")
    
    with col5:
        if 'Call_Purpose' in data.columns:
            daily_cancellation_rate = (cancellation_calls / total_calls * 100) if total_calls > 0 else 0
            st.metric("Daily Cancel Rate", f"{daily_cancellation_rate:.1f}%")
        else:
            st.metric("Daily Cancel Rate", "No transcript data")
    
    # 4. NO-SHOWS DASHBOARD
    st.subheader("⏰ 4. No-Shows Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Call_Purpose' in data.columns:
            # No-Show Distribution
            noshow_calls = data[data['Call_Purpose'] == 'No-Show Followup'].shape[0]
            show_calls = total_calls - noshow_calls
            
            fig = px.pie(
                values=[noshow_calls, show_calls],
                names=['No-Show Followups', 'Other Calls'],
                title="No-Show Followup Calls Distribution",
                color_discrete_sequence=['orange', 'lightgreen']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No-show analysis requires transcript data")
    
    with col2:
        if 'Call_Purpose' in data.columns:
            # No-Show Patterns
            purpose_noshow = data[data['Call_Purpose'] == 'No-Show Followup']
            if len(purpose_noshow) > 0:
                # Simple pattern analysis
                patterns = {
                    'First Time': purpose_noshow['transcript'].str.contains('first', na=False, case=False).sum(),
                    'Follow-up': purpose_noshow['transcript'].str.contains('follow', na=False, case=False).sum(),
                    'Reminder': purpose_noshow['transcript'].str.contains('remind', na=False, case=False).sum()
                }
                
                fig = px.pie(
                    values=list(patterns.values()),
                    names=list(patterns.keys()),
                    title="No-Show Call Patterns",
                    color_discrete_sequence=px.colors.sequential.Oranges
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No no-show patterns detected")
        else:
            st.info("No-show patterns require transcript data")
    
    # No-Show Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if 'Call_Purpose' in data.columns:
            noshow_calls = data[data['Call_Purpose'] == 'No-Show Followup'].shape[0]
            st.metric("No-Show Calls", noshow_calls)
        else:
            st.metric("No-Show Calls", "No transcript data")
    
    with col2:
        if 'Call_Purpose' in data.columns:
            total_calls = len(data)
            noshow_rate = (noshow_calls / total_calls * 100) if total_calls > 0 else 0
            st.metric("No-Show Rate", f"{noshow_rate:.1f}%")
        else:
            st.metric("No-Show Rate", "No transcript data")
    
    with col3:
        if 'Call_Purpose' in data.columns:
            first_time_noshow = data['transcript'].str.contains('first time', na=False, case=False).sum()
            st.metric("First Time No-Shows", first_time_noshow)
        else:
            st.metric("First Time No-Shows", "No transcript data")
    
    with col4:
        if 'Call_Purpose' in data.columns:
            followup_calls = data['transcript'].str.contains('follow up', na=False, case=False).sum()
            st.metric("Follow-up Calls", followup_calls)
        else:
            st.metric("Follow-up Calls", "No transcript data")
    
    with col5:
        if 'Call_Purpose' in data.columns:
            reminder_calls = data['transcript'].str.contains('remind', na=False, case=False).sum()
            st.metric("Reminder Calls", reminder_calls)
        else:
            st.metric("Reminder Calls", "No transcript data")
    
    # 5. RESPONSE TIMES DASHBOARD
    st.subheader("⚡ 5. Response Times Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        duration_cols = [col for col in data.columns if 'duration' in col.lower()]
        if duration_cols:
            # Ring Duration Distribution
            fig = px.histogram(
                data, 
                x=duration_cols[0],
                title="Ring Duration Distribution",
                nbins=20,
                color_discrete_sequence=['blue']
            )
            fig.add_vline(x=data[duration_cols[0]].mean(), line_dash="dash", 
                         line_color="red", annotation_text="Average")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Duration data not available for response time analysis")
    
    with col2:
        if duration_cols:
            # Response Time Categories
            fast_response = data[data[duration_cols[0]] <= 15].shape[0]
            medium_response = data[(data[duration_cols[0]] > 15) & (data[duration_cols[0]] <= 30)].shape[0]
            slow_response = data[data[duration_cols[0]] > 30].shape[0]
            
            fig = px.pie(
                values=[fast_response, medium_response, slow_response],
                names=['Fast (<15s)', 'Medium (15-30s)', 'Slow (>30s)'],
                title="Response Time Categories",
                color_discrete_sequence=['green', 'yellow', 'red']
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Response time categories require duration data")
    
    # Response Time Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if duration_cols and 'ring' in duration_cols[0].lower():
            avg_ring = data[duration_cols[0]].mean()
            st.metric("Avg Ring Time", f"{avg_ring:.1f}s")
        else:
            st.metric("Avg Ring Time", "N/A")
    
    with col2:
        if duration_cols and any('conversation' in col.lower() for col in duration_cols):
            conv_col = [col for col in duration_cols if 'conversation' in col.lower()][0]
            avg_conv = data[conv_col].mean()
            st.metric("Avg Call Time", f"{avg_conv:.1f}s")
        else:
            st.metric("Avg Call Time", "N/A")
    
    with col3:
        if duration_cols and any('total' in col.lower() for col in duration_cols):
            total_col = [col for col in duration_cols if 'total' in col.lower()][0]
            avg_total = data[total_col].mean()
            st.metric("Avg Total Time", f"{avg_total:.1f}s")
        else:
            st.metric("Avg Total Time", "N/A")
    
    with col4:
        if duration_cols:
            max_duration = data[duration_cols[0]].max()
            st.metric("Longest Call", f"{max_duration:.1f}s")
        else:
            st.metric("Longest Call", "N/A")
    
    with col5:
        if duration_cols:
            min_duration = data[duration_cols[0]].min()
            st.metric("Shortest Call", f"{min_duration:.1f}s")
        else:
            st.metric("Shortest Call", "N/A")
    
    # =================================================================
    # 2. QUALITATIVE METRICS DASHBOARD
    # =================================================================
    
    st.header("🎨 QUALITATIVE METRICS")
    
    # 1. SENTIMENT SUMMARIES DASHBOARD
    st.subheader("😊 Sentiment Summaries")
    
    if 'Sentiment' in data.columns:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Sentiment Distribution Pie Chart
            sentiment_counts = data['Sentiment'].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Call Sentiment Distribution",
                color=sentiment_counts.index,
                color_discrete_map={'Positive': '#00FF00', 'Neutral': '#FFFF00', 'Negative': '#FF0000'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment Metrics
            st.metric("Positive Calls", f"{(data['Sentiment'] == 'Positive').sum()}")
            st.metric("Neutral Calls", f"{(data['Sentiment'] == 'Neutral').sum()}")
            st.metric("Negative Calls", f"{(data['Sentiment'] == 'Negative').sum()}")
            
            positive_rate = (data['Sentiment'] == 'Positive').mean() * 100
            st.metric("Positive Rate", f"{positive_rate:.1f}%")
        
        with col3:
            # Sentiment Insights
            st.write("**📈 Sentiment Insights:**")
            if 'Call_Purpose' in data.columns:
                # Find purposes with highest negative sentiment
                sentiment_by_purpose = data.groupby('Call_Purpose')['Sentiment'].value_counts().unstack(fill_value=0)
                for purpose in sentiment_by_purpose.index:
                    if 'Negative' in sentiment_by_purpose.columns:
                        negative_pct = (sentiment_by_purpose.loc[purpose, 'Negative'] / sentiment_by_purpose.loc[purpose].sum() * 100)
                        if negative_pct > 30:  # Highlight high negative sentiment
                            st.write(f"⚠️ {purpose}: {negative_pct:.1f}% negative")
            
            # Overall sentiment score
            sentiment_score = ((data['Sentiment'] == 'Positive').sum() - (data['Sentiment'] == 'Negative').sum()) / len(data) * 100
            st.metric("Net Sentiment Score", f"{sentiment_score:.1f}")
    
    # 2. EMOTION ANALYSIS DASHBOARD
    st.subheader("💭 Emotion Analysis")
    
    if 'Emotions' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Emotion Frequency Chart
            all_emotions = []
            for emotions_list in data['Emotions']:
                all_emotions.extend(emotions_list)
            
            if all_emotions:
                emotion_counts = pd.Series(all_emotions).value_counts()
                fig = px.bar(
                    x=emotion_counts.values,
                    y=emotion_counts.index,
                    title="Most Common Emotions Detected",
                    orientation='h',
                    color=emotion_counts.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(xaxis_title="Frequency", yaxis_title="Emotions")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No specific emotions detected in calls")
        
        with col2:
            # Emotion by Call Purpose
            if 'Call_Purpose' in data.columns:
                emotion_purpose_data = []
                for purpose in data['Call_Purpose'].unique():
                    purpose_emotions = []
                    for idx, row in data[data['Call_Purpose'] == purpose].iterrows():
                        purpose_emotions.extend(row['Emotions'])
                    if purpose_emotions:
                        most_common_emotion = pd.Series(purpose_emotions).mode()
                        if len(most_common_emotion) > 0:
                            emotion_purpose_data.append({
                                'Purpose': purpose,
                                'Most_Common_Emotion': most_common_emotion[0],
                                'Emotion_Count': len(purpose_emotions)
                            })
                
                if emotion_purpose_data:
                    emotion_df = pd.DataFrame(emotion_purpose_data)
                    fig = px.bar(
                        emotion_df,
                        x='Purpose',
                        y='Emotion_Count',
                        color='Most_Common_Emotion',
                        title="Emotions by Call Purpose",
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    st.plotly_chart(fig, use_container_width=True)
    
    # 3. AI GENERATED NARRATIVES DASHBOARD
    st.subheader("📝 AI Generated Narratives")
    
    if 'Sentiment' in data.columns and 'Call_Purpose' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**📖 Patient Experience Story:**")
            total_calls = len(data)
            positive_calls = (data['Sentiment'] == 'Positive').sum()
            negative_calls = (data['Sentiment'] == 'Negative').sum()
            
            st.write(f"- **{positive_calls} calls ({positive_calls/total_calls*100:.1f}%)** showed positive patient satisfaction")
            st.write(f"- **{negative_calls} calls ({negative_calls/total_calls*100:.1f}%)** indicated service improvement opportunities")
            
            # Find most positive call purposes
            positive_purposes = data[data['Sentiment'] == 'Positive']['Call_Purpose'].value_counts().head(3)
            if len(positive_purposes) > 0:
                st.write("- **Most positive experiences** in:")
                for purpose, count in positive_purposes.items():
                    st.write(f"  - {purpose} ({count} calls)")
        
        with col2:
            st.info("**🎯 Service Quality Insights:**")
            
            # Sentiment trends by purpose
            if 'Call_Purpose' in data.columns:
                purpose_sentiment = data.groupby('Call_Purpose')['Sentiment'].value_counts().unstack(fill_value=0)
                
                # Find purposes needing attention
                high_negative = purpose_sentiment[purpose_sentiment['Negative'] / purpose_sentiment.sum(axis=1) > 0.2]
                if len(high_negative) > 0:
                    st.write("- **Areas needing attention:**")
                    for purpose in high_negative.index:
                        negative_rate = (purpose_sentiment.loc[purpose, 'Negative'] / purpose_sentiment.loc[purpose].sum() * 100)
                        st.write(f"  - {purpose}: {negative_rate:.1f}% negative sentiment")
                
                # Find service strengths
                high_positive = purpose_sentiment[purpose_sentiment['Positive'] / purpose_sentiment.sum(axis=1) > 0.6]
                if len(high_positive) > 0:
                    st.write("- **Service strengths:**")
                    for purpose in high_positive.index:
                        positive_rate = (purpose_sentiment.loc[purpose, 'Positive'] / purpose_sentiment.loc[purpose].sum() * 100)
                        st.write(f"  - {purpose}: {positive_rate:.1f}% positive sentiment")
    
    # 4. CALL QUALITY OBSERVATIONS DASHBOARD
    st.subheader("🔍 Call Quality Observations")
    
    if 'Call_Quality' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Call Quality Distribution
            quality_counts = data['Call_Quality'].value_counts()
            fig = px.pie(
                values=quality_counts.values,
                names=quality_counts.index,
                title="Call Quality Assessment",
                color=quality_counts.index,
                color_discrete_map={
                    'Excellent': '#00FF00', 
                    'Good': '#90EE90', 
                    'Average': '#FFFF00',
                    'Needs Improvement': '#FFA500',
                    'Poor': '#FF0000'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Quality Metrics and Insights
            st.write("**📊 Quality Metrics:**")
            excellent_calls = (data['Call_Quality'] == 'Excellent').sum()
            poor_calls = (data['Call_Quality'] == 'Poor').sum()
            total_calls = len(data)
            
            st.metric("Excellent Quality", f"{excellent_calls} calls ({(excellent_calls/total_calls*100):.1f}%)")
            st.metric("Needs Improvement", f"{poor_calls} calls ({(poor_calls/total_calls*100):.1f}%)")
            
            st.write("**💡 Quality Insights:**")
            if 'Call_Purpose' in data.columns:
                # Find purposes with best/worst quality
                quality_by_purpose = data.groupby('Call_Purpose')['Call_Quality'].value_counts().unstack(fill_value=0)
                best_quality = quality_by_purpose['Excellent'].idxmax() if 'Excellent' in quality_by_purpose.columns else None
                worst_quality = quality_by_purpose['Poor'].idxmax() if 'Poor' in quality_by_purpose.columns else None
                
                if best_quality:
                    st.write(f"- ✅ **Best quality**: {best_quality} calls")
                if worst_quality:
                    st.write(f"- ❌ **Needs training**: {worst_quality} handling")
    
    # SENTIMENT SAMPLE DATA
    st.subheader("🔍 AI Analysis Sample")
    if 'Sentiment' in data.columns and 'Emotions' in data.columns:
        sample_cols = ['transcript', 'Call_Purpose', 'Sentiment', 'Emotions']
        if 'Call_Quality' in data.columns:
            sample_cols.append('Call_Quality')
        if 'Booking_Success' in data.columns:
            sample_cols.append('Booking_Success')
        
        available_cols = [col for col in sample_cols if col in data.columns]
        st.dataframe(data[available_cols].head(8), use_container_width=True)

else:
    st.info("👆 Please upload your call data CSV file to begin analysis")
# =================================================================
# AI PROMPTS FOR CALL CLASSIFICATION
# =================================================================

st.header("🤖 AI CLASSIFICATION PROMPTS")

st.write("""
**Below are the actual prompts used to classify call transcripts into business-relevant categories. 
These prompts analyze conversation content to automatically categorize calls for analytics.**
""")

# 1. CALL PURPOSE CLASSIFICATION PROMPT
st.subheader("🎯 1. Call Purpose Classification Prompt")

purpose_prompt = """
ANALYZE THIS DENTAL PRACTICE PHONE CALL TRANSCRIPT AND CLASSIFY ITS PRIMARY PURPOSE.

CATEGORIES:
- APPOINTMENT BOOKING: Patient wants to schedule new appointment, asks about availability, books cleaning/checkup
- APPOINTMENT CANCELLATION: Patient cancels existing appointment, says they can't make it
- APPOINTMENT RESCHEDULE: Patient wants to change appointment date/time, move to different slot
- BILLING QUESTION: Questions about charges, payments, outstanding balances, payment plans
- INSURANCE VERIFICATION: Asks about insurance coverage, benefits, what's covered, claims
- CLINICAL QUESTION: Medical/dental health questions, symptoms, treatment options, pain concerns
- EMERGENCY: Urgent dental issues, severe pain, broken tooth, immediate care needed
- GENERAL INQUIRY: Office hours, location, services offered, doctor information, non-urgent questions
- FOLLOW-UP: Checking on previous treatment, post-operative care, healing progress

INSTRUCTIONS:
1. Read the entire transcript carefully
2. Identify the MAIN reason for the call
3. Choose ONLY ONE primary category
4. Return ONLY the category name in uppercase
5. If uncertain, choose the most likely category based on key phrases

TRANSCRIPT TO ANALYZE:
{transcript}

RETURN ONLY THE CATEGORY NAME:
"""

st.code(purpose_prompt, language='text')
st.caption("This prompt analyzes call transcripts to automatically categorize call purposes for tracking booking rates, cancellation patterns, and service demand.")

# 2. BOOKING SUCCESS DETECTION PROMPT
st.subheader("✅ 2. Booking Success Detection Prompt")

booking_success_prompt = """
DETERMINE IF THIS APPOINTMENT BOOKING CALL RESULTED IN A SUCCESSFUL SCHEDULING.

ANALYZE THE CALL TRANSCRIPT FOR:
- SUCCESS INDICATORS: "scheduled", "confirmed", "see you then", "thank you", "perfect", "great"
- FAILURE INDICATORS: "call back", "think about it", "check schedule", "maybe", "not sure"
- UNCLEAR: Inconclusive outcome, need to verify, ambiguous response

CATEGORIES:
- SUCCESSFUL: Appointment was clearly scheduled and confirmed
- FAILED: Patient declined, postponed, or didn't commit
- UNCLEAR: Outcome cannot be determined from transcript

INSTRUCTIONS:
1. Focus on the call conclusion and final agreement
2. Look for explicit confirmation or decline language
3. Consider the overall tone and commitment level
4. Return ONLY one word: SUCCESSFUL, FAILED, or UNCLEAR

TRANSCRIPT:
{transcript}

RESULT:
"""

st.code(booking_success_prompt, language='text')
st.caption("This prompt specifically tracks booking conversion rates by detecting successful vs failed appointment scheduling attempts.")

# 3. SENTIMENT ANALYSIS PROMPT
st.subheader("😊 3. Sentiment Analysis Prompt")

sentiment_prompt = """
ANALYZE THE PATIENT'S EMOTIONAL TONE AND SATISFACTION LEVEL IN THIS DENTAL CALL.

EMOTIONAL INDICATORS TO CONSIDER:

POSITIVE INDICATORS:
- Gratitude: "thank you", "appreciate", "helpful"
- Satisfaction: "great", "good", "perfect", "happy"
- Relief: "better", "helped", "improved"
- Enthusiasm: "excellent", "wonderful", "awesome"

NEGATIVE INDICATORS:
- Frustration: "angry", "frustrated", "annoyed"
- Disappointment: "not happy", "disappointed", "upset"
- Anxiety: "worried", "nervous", "scared", "concerned"
- Complaints: "problem", "issue", "complaint", "bad"

NEUTRAL INDICATORS:
- Factual questions without emotional language
- Routine inquiries about information
- Balanced or mixed emotional expressions

CATEGORIES:
- POSITIVE: Predominantly satisfied, grateful, or happy tone
- NEGATIVE: Clearly frustrated, angry, or dissatisfied
- NEUTRAL: Factual, balanced, or minimal emotional expression

INSTRUCTIONS:
1. Analyze the patient's language and emotional cues
2. Consider the overall tone, not just individual words
3. Return ONLY one word: POSITIVE, NEGATIVE, or NEUTRAL

TRANSCRIPT:
{transcript}

SENTIMENT:
"""

st.code(sentiment_prompt, language='text')
st.caption("This prompt assesses patient satisfaction and emotional state to track service quality and identify improvement areas.")

# 4. EMERGENCY DETECTION PROMPT
st.subheader("🚨 4. Emergency Detection Prompt")

emergency_prompt = """
DETECT IF THIS DENTAL CALL REQUIRES URGENT OR EMERGENCY ATTENTION.

URGENCY INDICATORS:
- Severe pain descriptors: "extreme pain", "can't sleep", "unbearable"
- Trauma indicators: "broken tooth", "knocked out", "accident", "injury"
- Infection signs: "swelling", "fever", "pus", "infection"
- Time sensitivity: "need to see someone today", "emergency", "as soon as possible"

ROUTINE INDICATORS:
- Preventive care: "cleaning", "checkup", "routine exam"
- Non-urgent issues: "small cavity", "next available", "when convenient"
- General questions: "information", "prices", "insurance"

CATEGORIES:
- EMERGENCY: Requires immediate same-day attention
- URGENT: Should be seen within 24-48 hours  
- ROUTINE: Can wait for next available appointment

INSTRUCTIONS:
1. Identify pain level and symptom severity
2. Look for time-sensitive language
3. Assess potential health risks
4. Return ONLY one category: EMERGENCY, URGENT, or ROUTINE

TRANSCRIPT:
{transcript}

URGENCY LEVEL:
"""

st.code(emergency_prompt, language='text')
st.caption("This prompt prioritizes calls based on medical urgency to ensure proper patient triage and care.")

# 5. INSURANCE & BILLING SPECIFIC PROMPT
st.subheader("💳 5. Insurance & Billing Classification Prompt")

insurance_prompt = """
CLASSIFY THE SPECIFIC TYPE OF FINancial OR INSURANCE INQUIRY IN THIS DENTAL CALL.

SUBCATEGORIES:

INSURANCE-RELATED:
- COVERAGE VERIFICATION: "Does my insurance cover this?", "What's covered?"
- BENEFITS CHECK: "What are my benefits?", "Annual maximum", "Deductible"
- CLAIMS STATUS: "Claim status", "When will I get paid?", "Processing time"
- NETWORK QUESTIONS: "Are you in-network?", "Preferred provider"

BILLING-RELATED:
- PAYMENT PLANS: "Payment options", "Installments", "Financing"
- OUTSTANDING BALANCE: "Outstanding bill", "Past due", "Collection"
- COST ESTIMATES: "How much will this cost?", "Price", "Fee"
- STATEMENT QUESTIONS: "Explanation of benefits", "Bill clarification"

CATEGORIES:
- INSURANCE_COVERAGE
- INSURANCE_CLAIMS  
- INSURANCE_NETWORK
- BILLING_PAYMENT
- BILLING_COST
- BILLING_STATEMENT

INSTRUCTIONS:
1. Identify the specific financial concern
2. Differentiate between insurance vs direct billing questions
3. Choose the most precise subcategory
4. Return ONLY the category name in uppercase

TRANSCRIPT:
{transcript}

FINANCIAL_CATEGORY:
"""

st.code(insurance_prompt, language='text')
st.caption("This prompt provides granular analysis of financial inquiries to optimize billing processes and insurance handling.")

# 6. NEW VS EXISTING PATIENT DETECTION
st.subheader("👥 6. New vs Existing Patient Detection Prompt")

patient_type_prompt = """
DETERMINE IF THE CALLER IS A NEW PATIENT OR EXISTING PATIENT.

NEW PATIENT INDICATORS:
- First-time mentions: "first time", "new patient", "never been there"
- Practice discovery: "found you online", "recommended by", "looking for dentist"
- Introductory questions: "tell me about your practice", "what services"
- No history: No references to previous visits or treatments

EXISTING PATIENT INDICATORS:
- Previous treatment references: "last time I was here", "my previous cleaning"
- Familiarity with staff: "Dr. Smith", "the hygienist", "receptionist"
- Continuity of care: "follow-up", "continued treatment", "next appointment"
- Personal history: References to their dental history with the practice

CATEGORIES:
- NEW_PATIENT: First-time caller seeking to establish care
- EXISTING_PATIENT: Current patient of the practice
- UNCLEAR: Cannot determine patient status from transcript

INSTRUCTIONS:
1. Look for explicit statements about patient history
2. Notice familiarity with practice and staff
3. Consider context of the inquiry
4. Return ONLY: NEW_PATIENT, EXISTING_PATIENT, or UNCLEAR

TRANSCRIPT:
{transcript}

PATIENT_TYPE:
"""

st.code(patient_type_prompt, language='text')
st.caption("This prompt distinguishes between new and existing patients to track acquisition success and retention rates.")

# PROMPT IMPLEMENTATION EXPLANATION
st.subheader("🔧 How These Prompts Work Together")

st.write("""
**Integrated Classification System:**

1. **Primary Purpose Detection** → Categorizes the main reason for call
2. **Sub-category Refinement** → Provides detailed classification within categories  
3. **Success Tracking** → Measures outcomes for business metrics
4. **Sentiment Analysis** → Monitors patient satisfaction
5. **Patient Type Identification** → Tracks acquisition vs retention

**Business Applications:**
- **Automated Call Routing**: Direct calls to appropriate departments
- **Performance Analytics**: Track conversion rates by call type
- **Staff Training**: Identify common scenarios needing improvement
- **Resource Allocation**: Understand demand for different services
- **Quality Assurance**: Monitor patient satisfaction trends

**Technical Implementation:**
- Each prompt analyzes the 'transcript' column from your CSV data
- Returns standardized categories for consistent reporting
- Enables automated dashboard metrics without manual review
- Scales to handle thousands of calls with consistent accuracy
""")

# SHOW SAMPLE CLASSIFICATION
#st.subheader("🔍 Sample Classification Output")

#if 'transcript' in data.columns and 'Call_Purpose' in data.columns:
    #sample_data = data[['transcript', 'Call_Purpose', 'Sentiment']].head(3).copy()
    
    #for idx, row in sample_data.iterrows():
        #with st.expander(f"Sample Call {idx+1}: {row['Call_Purpose']} - {row['Sentiment']}"):
            #st.write("**Transcript:**")
            #st.write(row['transcript'][:200] + "..." if len(row['transcript']) > 200 else row['transcript'])
            
            #st.write(f"**AI Classification:** {row['Call_Purpose']}")
            #st.write(f"**Sentiment Analysis:** {row['Sentiment']}")
            #st.write("**Prompt Used:** Call Purpose Classification + Sentiment Analysis")
#else:
    #st.info("Upload call data with transcripts to see AI classification examples")

# Footer
st.markdown("---")
st.markdown("**Built for Voicestack Applied AI Engineer**")