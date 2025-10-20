def show_ollama_metrics():
    """Show Ollama model info and metrics"""
    st.header("🤖 Ollama Status")
    
    # Initialize Ollama agent for metrics
    config = load_config()
    ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    ollama_model = os.getenv('OLLAMA_MODEL', config.get('ai', {}).get('ollama_model', 'llama3.1:8b'))
    
    agent = OllamaAgent(
        base_url=ollama_url,
        model=ollama_model,
        warmup=False  # Don't warm up for metrics check
    )
    
    # Create two columns
    col1, col2 = st.columns(2)
    
    # Model Information
    with col1:
        st.subheader("Model Information")
        model_info = agent.get_model_info()
        
        if model_info:
            st.markdown(f"""
            **Model:** {model_info.get('name', 'N/A')}  
            **Status:** {model_info.get('status', 'unknown')}  
            **Size:** {model_info.get('size', 0) / (1024*1024*1024):.2f} GB  
            **Last Modified:** {model_info.get('modified_at', 'N/A')}  
            """)
            
            details = model_info.get('details', {})
            if details:
                st.markdown("**Details:**")
                st.json(details)
        else:
            st.warning("⚠️ Could not fetch model information")
    
    # Resource Usage
    with col2:
        st.subheader("Resource Usage")
        metrics = agent.get_system_metrics()
        
        if metrics['process_status'] == 'running':
            # CPU Usage
            cpu_fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = metrics['cpu_percent'],
                title = {'text': "CPU Usage"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgray"},
                            {'range': [30, 70], 'color': "gray"},
                            {'range': [70, 100], 'color': "darkgray"}],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': metrics['cpu_percent']}}))
            st.plotly_chart(cpu_fig, use_container_width=True)
            
            # Memory Usage
            memory_fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = metrics['memory_percent'],
                title = {'text': f"Memory Usage ({metrics['memory_mb']:.0f} MB)"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                gauge = {'axis': {'range': [0, 100]},
                        'steps': [
                            {'range': [0, 30], 'color': "lightgray"},
                            {'range': [30, 70], 'color': "gray"},
                            {'range': [70, 100], 'color': "darkgray"}],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': metrics['memory_percent']}}))
            st.plotly_chart(memory_fig, use_container_width=True)
            
            # GPU Usage (if available)
            if metrics['gpu_utilization'] != 'N/A':
                gpu_value = float(metrics['gpu_utilization'].strip('%'))
                gpu_fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = gpu_value,
                    title = {'text': "GPU Usage"},
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {'axis': {'range': [0, 100]},
                            'steps': [
                                {'range': [0, 30], 'color': "lightgray"},
                                {'range': [30, 70], 'color': "gray"},
                                {'range': [70, 100], 'color': "darkgray"}],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': gpu_value}}))
                st.plotly_chart(gpu_fig, use_container_width=True)
        else:
            st.error("⚠️ Ollama process is not running")
            if metrics['process_status'] == 'error':
                st.warning("Could not fetch resource metrics")