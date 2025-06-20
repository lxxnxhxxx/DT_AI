import streamlit as st
import zipfile
import os
import json
import google.generativeai as genai
import tempfile

# Gemini API 설정
genai.configure(api_key="AIzaSyA6m8hPy_mCEOkOZ3YsrUEEqbs376N3Lwc")
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("📦 ZIP 기반 논문 분석 시스템")

uploaded_zip = st.file_uploader("논문 JSON 파일들이 들어있는 ZIP 파일을 업로드하세요", type=["zip"])
question = st.text_input("AI에게 물어볼 질문을 입력하세요:")

ask = st.button("질문하기")

if uploaded_zip and question and ask:
    try:
        context_list = []

        # 임시 폴더에 ZIP 파일 풀기
        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

            for filename in os.listdir(temp_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(temp_dir, filename), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        sections = data["packages"]["gpt"]["sections"]
                        title = sections.get("title", "")
                        abstract = sections.get("abstract", "")
                        method = sections.get("methodology", "")
                        result = sections.get("results", "")
                        context_list.append(
                            f"📄 제목: {title}\n[초록]\n{abstract}\n[방법론]\n{method}\n[결과]\n{result}\n"
                        )

        full_context = "\n\n---\n\n".join(context_list)

        prompt = f"""
다음은 여러 논문에서 추출한 핵심 내용입니다. 이 내용을 바탕으로 아래 질문에 답해주세요.

{full_context}

[질문]
{question}
"""

        response = model.generate_content(prompt)
        st.subheader("🧠 AI의 응답:")
        st.write(response.text)

    except Exception as e:
        st.error(f"❗ 오류 발생: {str(e)}")
