"""Streamlit web UI for dataset generation."""
import streamlit as st
import jsonlines
import uuid
import random
from pathlib import Path

from src.generators.pinescript import generate_pinescript
from src.generators.price_action import generate_price_action
from src.generators.institutional import generate_institutional
from src.schemas import TrainingExample

st.set_page_config(page_title="Trading Dataset Generator", page_icon="📊", layout="wide")

st.title("📊 Trading Dataset Generator")
st.markdown("Generate high-quality LLM training datasets for trading domain")

# Sidebar configuration
st.sidebar.header("Configuration")
dataset_size = st.sidebar.number_input("Dataset Size", min_value=10, max_value=100000, value=100, step=10)
seed_value = st.sidebar.number_input("Random Seed (0=random)", min_value=0, max_value=999999, value=0)
balance_categories = st.sidebar.checkbox("Balance Categories", value=True)

st.sidebar.markdown("---")
st.sidebar.header("Category Weights")
if not balance_categories:
    pine_weight = st.sidebar.slider("PineScript %", 0, 100, 30)
    price_weight = st.sidebar.slider("Price Action %", 0, 100, 40)
    inst_weight = 100 - pine_weight - price_weight
    st.sidebar.write(f"Institutional: {inst_weight}%")
else:
    pine_weight = price_weight = inst_weight = 33

# Main content
tab1, tab2, tab3 = st.tabs(["Generate", "Preview", "Validate"])

with tab1:
    st.header("Generate Dataset")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Samples", dataset_size)
        st.metric("PineScript", int(dataset_size * pine_weight / 100))
    with col2:
        st.metric("Price Action", int(dataset_size * price_weight / 100))
        st.metric("Institutional", int(dataset_size * inst_weight / 100))
    
    output_name = st.text_input("Output Filename", value="trading_dataset.jsonl")
    
    if st.button("🚀 Generate Dataset", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Setup
        actual_seed = seed_value if seed_value > 0 else random.randint(1, 999999)
        random.seed(actual_seed)
        
        distribution = {
            'pinescript': int(dataset_size * pine_weight / 100),
            'price_action': int(dataset_size * price_weight / 100),
            'institutional': int(dataset_size * inst_weight / 100)
        }
        
        generators = {
            'pinescript': generate_pinescript,
            'price_action': generate_price_action,
            'institutional': generate_institutional
        }
        
        # Generate
        samples = []
        total_generated = 0
        
        for category, count in distribution.items():
            status_text.text(f"Generating {category}...")
            for i in range(count):
                sample_seed = random.randint(0, 1000000)
                data = generators[category](seed=sample_seed)
                
                example = TrainingExample(
                    id=str(uuid.uuid4()),
                    instruction=data['instruction'],
                    response=data['response'],
                    pattern_type=data['pattern_type'],
                    timeframe=data.get('timeframe'),
                    seed=sample_seed,
                    metadata=data.get('metadata', {})
                )
                samples.append(example.model_dump())
                total_generated += 1
                progress_bar.progress(total_generated / dataset_size)
        
        # Shuffle and save
        random.shuffle(samples)
        output_path = Path("datasets") / output_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with jsonlines.open(output_path, mode='w') as writer:
            writer.write_all(samples)
        
        status_text.text("")
        progress_bar.empty()
        st.success(f"✓ Generated {len(samples)} samples → {output_path}")
        st.balloons()

with tab2:
    st.header("Preview Samples")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Generate PineScript Sample"):
            data = generate_pinescript()
            st.code(data['instruction'], language="text")
            st.code(data['response'], language="javascript")
    
    with col2:
        if st.button("Generate Price Action Sample"):
            data = generate_price_action()
            st.write(f"**Instruction:** {data['instruction']}")
            st.write(f"**Response:** {data['response']}")
    
    with col3:
        if st.button("Generate Institutional Sample"):
            data = generate_institutional()
            st.write(f"**Instruction:** {data['instruction']}")
            st.write(f"**Response:** {data['response']}")

with tab3:
    st.header("Validate Dataset")
    
    uploaded_file = st.file_uploader("Upload JSONL file", type=['jsonl'])
    
    if uploaded_file:
        errors = []
        valid_count = 0
        
        for i, line in enumerate(uploaded_file):
            try:
                import json
                obj = json.loads(line)
                TrainingExample(**obj)
                valid_count += 1
            except Exception as e:
                errors.append(f"Line {i+1}: {str(e)}")
        
        if errors:
            st.error(f"Found {len(errors)} errors")
            for err in errors[:20]:
                st.text(err)
        else:
            st.success(f"✓ All {valid_count} samples are valid!")
