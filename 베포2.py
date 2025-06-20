import streamlit as st
import zipfile
import os
import json
import google.generativeai as genai
import tempfile

# Gemini API 설정
genai.configure(api_key="AIzaSyA6m8hPy_mCEOkOZ3YsrUEEqbs376N3Lwc")
model = genai.GenerativeModel("gemini-1.5-flash")

st.title("📄 JSON/ZIP 기반 논문 분석 시스템")

uploaded_file = st.file_uploader(
    "논문 JSON 파일들을 업로드하세요 (ZIP 또는 JSON)",
    type=["zip", "json"]
)
question = st.text_input("AI에게 물어볼 질문을 입력하세요:")

ask = st.button("질문하기")

if uploaded_file and question and ask:
    try:
        context_list = []

        with tempfile.TemporaryDirectory() as temp_dir:
            # ZIP 파일 처리
            if uploaded_file.type == "application/zip" or uploaded_file.name.lower().endswith(".zip"):
                with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)
                paths = [
                    os.path.join(temp_dir, fn)
                    for fn in os.listdir(temp_dir)
                    if fn.lower().endswith(".json")
                ]
            # 단일 JSON 처리
            else:
                path = os.path.join(temp_dir, uploaded_file.name)
                with open(path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                paths = [path]

            # 각 JSON 파싱
            for p in paths:
                with open(p, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # sections 위치 판별
                if isinstance(data.get("packages"), dict):
                    # 기존 구조: data["packages"]["gpt"]["sections"]
                    sections = (
                        data["packages"].get("gpt", {})
                                        .get("sections", {})
                    )
                else:
                    # 새 구조: data["sections"]
                    sections = data.get("sections", {})

                title       = sections.get("title", "")
                abstract    = sections.get("abstract", "")
                methodology = sections.get("methodology", "")
                results     = sections.get("results", "")

                context_list.append(
                    f"📄 제목: {title}\n\n"
                    f"[초록]\n{abstract}\n\n"
                    f"[방법론]\n{methodology}\n\n"
                    f"[결과]\n{results}"
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
