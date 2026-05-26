import re
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from sympy import lambdify, symbols, sympify

# Matplotlib 中文介面
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

# 頁面設定
st.set_page_config(page_title="數學函數繪圖程式", layout="wide")
st.title("數學函數繪圖")
st.write("可輸入函數並自動畫出圖形")

# 側邊欄設定
with st.sidebar:
    st.header("圖形設定")
    x_min, x_max = st.slider("X 軸範圍", -100, 100, (-10, 10))
    y_min, y_max = st.slider("Y 軸範圍", -100, 100, (-10, 10))
    show_grid = st.checkbox("顯示格線", value=True)
    line_color = st.color_picker("線條顏色", "#1f77b4")

# 輸入
user_input = st.text_area(
    "請輸入函數",
    placeholder="例如：y=x、e^x、x=1",
    height=100,
)
def clean_text(text):
    """整理輸入格式"""

    text = re.sub(r"\s+", "", text.lower().strip())

    # 移除常見文字
    noise_words = ["幫我畫", "畫出", "的圖", "函數", "圖形", "求解", "請", "個"]
    for word in noise_words:
        text = text.replace(word, "")

    # 中文轉數字
    zh_num_map = {
        "零": "0", "一": "1", "二": "2", "兩": "2", "三": "3",
        "四": "4", "五": "5", "六": "6", "七": "7", "八": "8", "九": "9"
    }
    for zh, num in zh_num_map.items():
        text = text.replace(zh, num)
    # 運算符號轉換
    op_map = {
        "加上": "+", "加": "+", "減掉": "-", "減": "-",
        "乘以": "*", "乘": "*", "除以": "/", "除": "/",
        "平方": "**2", "立方": "**3", "^": "**"
    }
    for zh, op in op_map.items():
        text = text.replace(zh, op)

    # e^x
    text = re.sub(r"e\*\*([a-z0-9\(]+)", r"E**(\1)", text)
    text = re.sub(r"e([a-z\(\)])", r"E*\1", text)

    text = text.replace("自然對數", "log")
    text = text.replace("ln", "log")

    # y=
    if text.startswith("y="):
        text = text[2:]
    elif text.startswith("y等於"):
        text = text[3:]

    # 自動補乘號
    text = re.sub(r"(\d)([a-zA-Z\(])", r"\1*\2", text)
    text = re.sub(r"([xE\)])([a-zA-Z\(])", r"\1*\2", text)

    return text


# 按鈕
if st.button("開始繪圖"):

    if not user_input:
        st.warning("請先輸入函數")
        st.stop()

    cleaned_str = clean_text(user_input)

    # 建立圖表
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)

    is_vertical_line = False
    v_line_val = 0.0

    # 判斷是否為x=數字
    v_match = re.match(r"^x=([\d\+\-\*\/\.]+)$", cleaned_str)

    if v_match:
        try:
            v_line_val = float(eval(v_match.group(1)))
            is_vertical_line = True
        except:
            pass

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("結果")

        st.info(f"原始輸入： {user_input}")
        st.success(f"整理後： `{cleaned_str}`")

        if is_vertical_line:
            st.write(f"偵測到垂直線： x = {v_line_val}")

        else:
            x = symbols("x")

            try:
                expr = sympify(cleaned_str)
                st.write("數學式：")
                st.latex(expr)

            except Exception:
                st.error("解析失敗")
                st.stop()

    with col2:
        st.subheader("函數圖形")

        # 設定比例
        ax.set_aspect('equal', adjustable='box')

        if is_vertical_line:
            ax.axvline(
                x=v_line_val,
                color=line_color,
                linewidth=2.5,
                label=f"x = {v_line_val}"
            )

        else:
            x_vals = np.linspace(x_min, x_max, 2000)

            try:
                f_lambdified = lambdify(x, expr, modules=["numpy"])
                y_vals = f_lambdified(x_vals)

                if isinstance(y_vals, (int, float)):
                    y_vals = np.full_like(x_vals, float(y_vals))

                else:
                    y_vals = np.asarray(y_vals, dtype=np.float64)

            except Exception:
                st.error("計算錯誤")
                st.stop()

            # 過濾極端值
            y_vals[y_vals > y_max * 10] = np.nan
            y_vals[y_vals < y_min * 10] = np.nan

            if "tan" in cleaned_str or "/" in cleaned_str:
                threshold = (y_max - y_min) * 50
                dy = np.abs(np.diff(y_vals, prepend=y_vals[0]))
                y_vals[dy > threshold] = np.nan

            ax.plot(
                x_vals,
                y_vals,
                color=line_color,
                linewidth=2.5,
                label=f"y = {expr}"
            )

        # 隱藏上方與右方邊框
        ax.spines['top'].set_color('none')
        ax.spines['right'].set_color('none')

        # 將座標軸移到原點
        ax.spines['bottom'].set_position(('data', 0))
        ax.spines['left'].set_position(('data', 0))

        # 座標軸樣式
        ax.spines['bottom'].set_linewidth(1.8)
        ax.spines['left'].set_linewidth(1.8)

        ax.spines['bottom'].set_color('#222222')
        ax.spines['left'].set_color('#222222')

        # 刻度位置
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')

        #範圍
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)

        # 格線
        if show_grid:
            ax.grid(True, linestyle="--", alpha=0.5)

        # 標題
        title_label = (
            f"x = {v_line_val}"
            if is_vertical_line
            else f"y = {expr}"
        )

        ax.set_title(f"函數圖形： {title_label}", fontsize=14, pad=20)

        #X、Y 標記
        ax.text(x_max * 0.95, y_max * 0.05, "X", fontsize=12)
        ax.text(x_max * 0.05, y_max * 0.95, "Y", fontsize=12)

        ax.legend(loc="upper right")

        # 顯示圖形
        st.pyplot(fig)
