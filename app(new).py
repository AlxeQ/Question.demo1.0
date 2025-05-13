import streamlit as st
import requests
import json
import urllib.parse

# 页面配置
st.set_page_config(
    page_title="商圈经理提问优化助手",
    page_icon="🏢",
    layout="centered"
)

# 自定义样式
st.markdown("""
<style>
.stTextArea textarea {
    min-height: 150px;
}
.result-block {
    background-color: #f9f9f9;
    padding: 1rem;
    border-radius: 0.5rem;
    white-space: pre-wrap;
    margin-top: 1rem;
}
.custom-prompt {
    border-left: 3px solid #007AFF;
    padding-left: 1rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# 应用标题
st.title("🏢 商圈经理提问优化助手")
st.caption("帮助商圈经理优化提问方式，获得更精准的业务建议")

# 初始化session状态
if "custom_prompt" not in st.session_state:
    st.session_state.custom_prompt = """你是一位"问题优化教练"，服务对象是链家商圈经理。当他们输入问题时，你需要：
1. 从"目标、背景、细节、期待"四个维度分析，指出提问中缺失或模糊的信息；
2. 针对每个维度，生成 3~5 条可选的引导词示例；
3. 基于上述分析，输出一版结构化完整的优化提问示范；
4. 用温和且专业的教练语气，不直接给业务答案，而是教他们如何精准提问。"""

# 自定义提示词区域
with st.expander("🛠️ 自定义系统提示词（高级选项）"):
    st.session_state.custom_prompt = st.text_area(
        "修改系统提示词以改变AI行为：",
        value=st.session_state.custom_prompt,
        height=200,
        help="此提示词将指导AI如何优化您的问题"
    )

# 输入区域
with st.form("question_form"):
    user_input = st.text_area(
        "请输入您要优化的问题：",
        placeholder="例如：我不知道怎么说服不配合的同事",
        help="描述您在工作中遇到的困惑或问题"
    )
    
    api_key = st.text_input(
        "DeepSeek API Key",
        type="password",
        placeholder="以 sk- 开头的密钥",
        help="请确保API Key有效且有足够额度"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        submitted = st.form_submit_button("🚀 生成优化提问", use_container_width=True)
    with col2:
        open_deepseek = st.form_submit_button("🌐 跳转DeepSeek", use_container_width=True)

# 处理跳转DeepSeek
if open_deepseek:
    if not user_input:
        st.error("请先输入问题")
    else:
        # 编码用户输入作为DeepSeek聊天参数
        encoded_query = urllib.parse.quote(user_input)
        deepseek_url = f"https://chat.deepseek.com/?q={encoded_query}"
        st.markdown(f'<meta http-equiv="refresh" content="0; url={deepseek_url}">', unsafe_allow_html=True)
        st.success("正在跳转到DeepSeek官网...")

# 处理提交
if submitted:
    if not user_input or not api_key:
        st.error("请填写问题和API Key")
        st.stop()
    
    with st.spinner("正在优化您的提问，请稍候..."):
        messages = [
            {
                "role": "system",
                "content": st.session_state.custom_prompt
            },
            {
                "role": "user",
                "content": f"""用户输入的问题是：“{user_input}”
请按照以下格式输出：
✅ 我理解你想问的是：…
🎯 目标：…
📍 背景：…
🔍 细节：…
✨ 期待：…

🧩 引导词示例：
- 目标：…
- 背景：…
- 细节：…
- 期待：…

📌 优化提问示范：“…”"""
            }
        ]
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            if data.get("choices") and data["choices"][0]:
                st.subheader("优化结果")
                result_content = data["choices"][0]["message"]["content"]
                st.markdown(f'<div class="result-block">{result_content}</div>', 
                           unsafe_allow_html=True)
                
                # 添加跳转按钮到结果区域
                encoded_result = urllib.parse.quote(result_content)
                st.link_button("💬 在DeepSeek中继续对话", 
                              f"https://chat.deepseek.com/?q={encoded_result}")
                
            else:
                st.error("API返回异常：" + json.dumps(data, ensure_ascii=False, indent=2))
                
        except requests.exceptions.RequestException as e:
            st.error(f"请求失败：{str(e)}")
        except Exception as e:
            st.error(f"处理出错：{str(e)}")

# 页脚说明
st.markdown("---")
st.caption("💡 提示：优化后的提问能帮助您获得更精准的业务建议")