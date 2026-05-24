import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from sympy import symbols, sympify


# 頁面設定

st.set_page_config(page_title="數學圖形生成系統")

st.title("數學圖形生成系統")

st.write("輸入數學題目，系統會自動分析並生成圖形。")


# 使用者輸入

user_input = st.text_area(
    "輸入題目",
    placeholder="例如：幫我畫 x平方減4x加3 的圖"
)


# 中文轉換

def convert_math_text(text):

    text = text.lower()

    # 去空白
    text = text.replace(" ", "")

    # 中文運算
    text = text.replace("加", "+")
    text = text.replace("減", "-")
    text = text.replace("乘", "*")
    text = text.replace("除", "/")

    # 次方
    text = text.replace("平方", "**2")
    text = text.replace("立方", "**3")

    # 三角函數
    text = text.replace("sinx", "sin(x)")
    text = text.replace("cosx", "cos(x)")
    text = text.replace("tanx", "tan(x)")

    # 數學格式
    text = text.replace("^", "**")

    # 中文描述
    text = text.replace("幫我畫", "")
    text = text.replace("畫", "")
    text = text.replace("的圖", "")
    text = text.replace("函數", "")

    # 自動補乘號
    text = text.replace("2x", "2*x")
    text = text.replace("3x", "3*x")
    text = text.replace("4x", "4*x")
    text = text.replace("5x", "5*x")
    text = text.replace("6x", "6*x")
    text = text.replace("7x", "7*x")
    text = text.replace("8x", "8*x")
    text = text.replace("9x", "9*x")

    return text


# 按鈕

if st.button("生成圖形"):

    if not user_input:
        st.warning("請先輸入題目")
        st.stop()


    # 文字轉函數

    function_str = convert_math_text(user_input)

    st.subheader("解析結果")
    st.code(function_str)


    # sympy 解析

    x = symbols('x')

    try:
        expr = sympify(function_str)

    except Exception as e:
        st.error("函數解析失敗")
        st.error(e)
        st.stop()


    # 建立資料點

    x_vals = np.linspace(-10, 10, 2000)

    y_vals = []

    for val in x_vals:

        try:

            y = expr.subs(x, val)

            y_float = float(y)

            # 避免 tan(x) 這種爆掉
            if abs(y_float) > 10:
                y_vals.append(np.nan)

            else:
                y_vals.append(y_float)

        except:

            y_vals.append(np.nan)


    # 畫圖

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x_vals, y_vals)

    # 座標軸
    ax.axhline(0, color='black')
    ax.axvline(0, color='black')

    # 格線
    ax.grid(True)

    # 限制 y 軸
    ax.set_ylim(-10, 10)

    # 標題
    ax.set_title(f"y = {function_str}")


    # 顯示圖形
    st.subheader("圖形")
    st.pyplot(fig)