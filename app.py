import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="학생명렬표 변환기", page_icon="📄", layout="centered")

st.title("학생명렬표 자동 변환기")
st.write("엑셀 파일을 업로드하면 업로드용 형식으로 자동 변환합니다.")

TWO_CHAR_LAST_NAMES = ["황보", "남궁", "제갈", "사공", "선우", "서문", "독고", "동방", "어금"]


def split_name(name):
    name = str(name).strip().replace(" ", "")
    for last_name in TWO_CHAR_LAST_NAMES:
        if name.startswith(last_name):
            return last_name, name[len(last_name):]
    if len(name) >= 2:
        return name[0], name[1:]
    return name, ""


def convert_gender(gender):
    gender = str(gender).strip()
    if gender == "남성":
        return "남자"
    if gender == "여성":
        return "여자"
    return gender


def convert_birth(birth):
    birth = str(birth).strip()
    return birth.replace(".", "").replace("-", "").replace("/", "").replace(" ", "")


uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(col).strip() for col in df.columns]

        required_cols = ["학년", "반", "번호", "성명", "성별", "생년월일"]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            st.error(f"필수 컬럼이 없습니다: {', '.join(missing_cols)}")
        else:
            result = pd.DataFrame()
            result["순번"] = range(1, len(df) + 1)
            result["학년"] = df["학년"]
            result["반"] = df["반"]
            result["번호"] = df["번호"]

            split_result = df["성명"].apply(split_name)
            result["성"] = split_result.apply(lambda x: x[0])
            result["이름"] = split_result.apply(lambda x: x[1])

            result["전체이름"] = df["성명"].astype(str).str.strip().str.replace(" ", "", regex=False)
            result["성별"] = df["성별"].apply(convert_gender)
            result["생년월일"] = df["생년월일"].apply(convert_birth)
            result["개인정보동의첨부파일제출여부"] = "Y"

            st.success("변환 완료!")
            st.dataframe(result)

            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                result.to_excel(writer, index=False, sheet_name="업로드용")
            output.seek(0)

            st.download_button(
                label="변환된 엑셀 다운로드",
                data=output,
                file_name="학생명렬표_업로드용.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")