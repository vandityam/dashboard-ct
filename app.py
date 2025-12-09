# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# =============================================================================
# KONFIGURASI DASHBOARD
# =============================================================================
st.set_page_config(page_title="Dashboard Bebras Challenge", layout="wide")


with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
st.title("Dashboard Hasil Bebras Challenge 2024")
st.markdown(
    "<p class='subtitle'>Visualisasi kemampuan <b>Computational Thinking</b> peserta SD, SMP, dan SMA berdasarkan hasil Bebras Challenge 2024.</p>",
    unsafe_allow_html=True
)

# =============================================================================
# LOAD DATA
# =============================================================================
@st.cache_data
def load_data():
    return pd.read_csv("files/dashboard_bebras.csv")

bebras = load_data()

# =============================================================================
# MAPPING (Provinsi → Kota & Kategori → Kelas)
# =============================================================================
mapping_kategori_kelas = (
    bebras[["Kategori", "Kelas"]]
    .drop_duplicates()
    .groupby("Kategori")["Kelas"]
    .apply(list)
    .to_dict()
)

mapping_prov_kota = (
    bebras[["Provinsi", "SekolahKotaKabupaten"]]
    .drop_duplicates()
    .groupby("Provinsi")["SekolahKotaKabupaten"]
    .apply(list)
    .to_dict()
)

# =============================================================================
# SIDEBAR FILTER
# =============================================================================
st.sidebar.header("🔍 Filter Data")

# ---- Provinsi ----
provinsi = st.sidebar.multiselect(
    "Pilih Provinsi:",
    sorted(bebras["Provinsi"].dropna().unique())
)

# ---- Kota ----
if provinsi:
    kota_allowed = sorted({k for p in provinsi for k in mapping_prov_kota.get(p, [])})
else:
    kota = st.sidebar.multiselect(
        "Pilih Kota/Kabupaten:",
        sorted(bebras["SekolahKotaKabupaten"].dropna().unique())
    )

# ---- Kategori ----
kategori = st.sidebar.multiselect(
    "Pilih Kategori:",
    sorted(bebras["Kategori"].dropna().unique())
)

# ---- Kelas ----
if kategori:
    kelas_allowed = sorted({k for cat in kategori for k in mapping_kategori_kelas.get(cat, [])})
else:
    kelas = st.sidebar.multiselect(
        "Pilih Kelas:",
        sorted(bebras["Kelas"].dropna().unique())
    )

# =============================================================================
# FILTER DATA UTAMA
# =============================================================================
filtered = bebras.copy()

if provinsi:
    filtered = filtered[filtered["Provinsi"].isin(provinsi)]
if kota:
    filtered = filtered[filtered["SekolahKotaKabupaten"].isin(kota)]
if kategori:
    filtered = filtered[filtered["Kategori"].isin(kategori)]
if kelas:
    filtered = filtered[filtered["Kelas"].isin(kelas)]

st.sidebar.write(f"Total data: **{len(filtered)} peserta**")

#=============================================================================
# INFORMASI FILTER AKTIF
#=============================================================================
active_filters = []
if provinsi: active_filters.append("Provinsi: " + ", ".join(provinsi))
if kota: active_filters.append("Kota: " + ", ".join(kota))
if kategori: active_filters.append("Kategori: " + ", ".join(kategori))
if kelas: active_filters.append("Kelas: " + ", ".join(kelas))

if active_filters:
    st.info("Filter aktif: " + " | ".join(active_filters))
else:
    st.info("Menampilkan seluruh data.")

# =============================================================================
# 1️⃣ KPI / STATISTIK RINGKAS
# =============================================================================
st.subheader("📈 Statistik Umum")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah Peserta", len(filtered))
col2.metric("Rata-rata Nilai", round(filtered["Nilai"].mean(), 2))
col3.metric("Nilai Tertinggi", round(filtered["Nilai"].max(), 2))
col4.metric("Nilai Terendah", round(filtered["Nilai"].min(), 2))
# =============================================================================
# 2️⃣ DISTRIBUSI PESERTA
# =============================================================================
st.markdown(
    """
    <div style="padding:4px 12px; background-color:#f8f9fa; border-radius:15px; margin-top:15px">
        <h3>👥 Distribusi Peserta</h3>
    </div>
    """,
    unsafe_allow_html=True
)

tab_demografi, tab_wilayah = st.tabs(["Demografi", "Wilayah"])

# ---------------------------
# TAB 1: DEMOGRAFI
# ---------------------------
with tab_demografi:
    col1, col2 = st.columns(2)

    # Pie Jenis Kelamin
    with col1:
        gender_counts = filtered["JenisKelamin"].value_counts().reset_index()
        gender_counts.columns = ["JenisKelamin", "Jumlah"]

        fig_gender = px.pie(
            gender_counts,
            values="Jumlah",
            names="JenisKelamin",
            title="Distribusi Berdasarkan Jenis Kelamin",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_gender, use_container_width=True)

    # Bar Kelas
    with col2:
        kelas_counts = filtered["Kelas"].value_counts().reset_index()
        kelas_counts.columns = ["Kelas", "Jumlah"]

        fig_kelas = px.bar(
            kelas_counts,
            x="Kelas",
            y="Jumlah",
            title="Distribusi Berdasarkan Kelas",
            color="Jumlah",
            color_continuous_scale="Teal"
        )
        fig_kelas.update_layout(showlegend=False)
        st.plotly_chart(fig_kelas, use_container_width=True)

# ---------------------------
# TAB 2: WILAYAH
# ---------------------------
with tab_wilayah:
    colw1, colw2 = st.columns(2)

    # Provinsi
    with colw1:
        prov_counts = (
            filtered["Provinsi"]
            .value_counts(dropna=False)
            .reset_index()
        )
        prov_counts.columns = ["Provinsi", "Jumlah"]

        fig_prov = px.bar(
            prov_counts,
            x="Jumlah",
            y="Provinsi",
            orientation="h",
            title="Distribusi Berdasarkan Provinsi",
            color="Jumlah",
            color_continuous_scale="Blues"
        )
        fig_prov.update_layout(
            showlegend=False,
            xaxis_title="Jumlah Peserta",
            yaxis_title="Provinsi"
        )
        st.plotly_chart(fig_prov, use_container_width=True)

    # Kota/Kabupaten
    with colw2:
        kota_counts = (
            filtered["SekolahKotaKabupaten"]
            .value_counts(dropna=False)
            .reset_index()
        )
        kota_counts.columns = ["Kota/Kabupaten", "Jumlah"]

        fig_kota = px.bar(
            kota_counts,  
            x="Jumlah",
            y="Kota/Kabupaten",
            orientation="h",
            title="Distribusi Berdasarkan Kota/Kabupaten",
            color="Jumlah",
            color_continuous_scale="Greens"
        )
        fig_kota.update_layout(
            showlegend=False,
            xaxis_title="Jumlah Peserta",
            yaxis_title="Kota/Kabupaten"
        )
        st.plotly_chart(fig_kota, use_container_width=True)


# =============================================================================
# 3️⃣ ANALISIS NILAI PESERTA
# =============================================================================
st.markdown(
    """
    <div style="padding:4px 12px; background-color:#f8f9fa; border-radius:15px; margin-top:15px">
        <h3>🎯 Analisis Nilai Peserta</h3>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["Distribusi Nilai", "Perbandingan", "Provinsi"])

# ---------------------------- TAB 1: DISTRIBUSI NILAI ----------------------------
with tab1:
    fig_hist = px.histogram(
        filtered,
        x="Nilai",
        nbins=10,
        title="Distribusi Nilai Peserta",
        color_discrete_sequence=["#82C9FF"]
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    fig_box = px.box(
        filtered,
        y="Nilai",
        title="Sebaran Nilai Peserta (Boxplot)"
    )
    st.plotly_chart(fig_box, use_container_width=True)

# -------------------------- TAB 2: PERBANDINGAN DEMOGRAFI --------------------------
with tab2:
    col1, col2, col3 = st.columns(3)

    # Gender
    with col1:
        fig_gender_score = px.box(
            filtered,
            x="JenisKelamin",
            y="Nilai",
            title="Nilai Berdasarkan Jenis Kelamin"
        )
        st.plotly_chart(fig_gender_score, use_container_width=True)

    # Kelas
    with col2:
        fig_kelas_score = px.box(
            filtered,
            x="Kelas",
            y="Nilai",
            title="Nilai Berdasarkan Kelas"
        )
        st.plotly_chart(fig_kelas_score, use_container_width=True)

    # Kategori
    with col3:
        df_avg_kat = (
            filtered.groupby("Kategori", as_index=False)["Nilai"]
            .mean()
            .sort_values("Nilai", ascending=False)
        )

        fig_kat_score = px.bar(
            df_avg_kat,
            x="Kategori",
            y="Nilai",
            title="Rata-rata Nilai per Kategori",
            color="Kategori",
            color_discrete_sequence=px.colors.qualitative.Vivid
        )
        st.plotly_chart(fig_kat_score, use_container_width=True)

# --------------------------- TAB 3: NILAI PROVINSI ---------------------------
with tab3:
    df_avg_prov = (
        filtered.groupby("Provinsi")["Nilai"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    fig_prov_score = px.bar(
        df_avg_prov,
        x="Nilai",
        y="Provinsi",
        orientation="h",
        title="Rata-rata Nilai per Provinsi",
        color="Nilai",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig_prov_score, use_container_width=True)

# ---------------------------------------------------------
# RATA-RATA NILAI PER SEKOLAH
# ---------------------------------------------------------
st.markdown(
    """
    <div style="padding:4px 12px; background-color:#f8f9fa; border-radius:15px; margin-top:15px">
        <h3>🏫 Rata-rata Nilai per Sekolah</h3>
    </div>
    """,
    unsafe_allow_html=True
)

df_school = (
    filtered.groupby("SekolahNama")["Nilai"]
    .mean()
    .reset_index()
    .sort_values("Nilai", ascending=False)
)

top_n = st.slider("Tampilkan Top-N Sekolah", 5, 30, 10)

fig_school = px.bar(
    df_school.head(top_n),
    x="Nilai",
    y="SekolahNama",
    orientation="h",
    title=f"Top {top_n} Sekolah Berdasarkan Rata-rata Nilai",
)
st.plotly_chart(fig_school, use_container_width=True)

# ---------------------------------------------------------
# PEMETAAN KEKUATAN & KELEMAHAN PESERTA — KATEGORI SOAL
# ---------------------------------------------------------
st.markdown(
    """
    <div style="padding:4px 12px; background-color:#f8f9fa; border-radius:15px; margin-top:15px">
        <h3>🎯 Kekuatan & Kelemahan Berdasarkan Kategori Soal</h3>
    </div>
    """,
    unsafe_allow_html=True
)

kategori_cols = [c for c in filtered.columns if c.startswith("S ") or c.startswith("S_")]

if len(kategori_cols) > 0:
    df_kat = filtered[kategori_cols].mean().reset_index()
    df_kat.columns = ["Kategori", "RataRata"]

    fig_kat = px.bar(
        df_kat,
        x="Kategori",
        y="RataRata",
        title="Rata-rata Nilai per Kategori Soal",
    )
    st.plotly_chart(fig_kat, use_container_width=True)

    # Insight otomatis
    kat_tertinggi = df_kat.sort_values("RataRata", ascending=False).iloc[0]
    kat_terendah = df_kat.sort_values("RataRata", ascending=True).iloc[0]

    st.success(
        f"""
        **Kekuatan terbesar peserta:**  
        🟩 *{kat_tertinggi['Kategori']}* — {kat_tertinggi['RataRata']:.2f}

        **Kelemahan terbesar peserta:**  
        🟥 *{kat_terendah['Kategori']}* — {kat_terendah['RataRata']:.2f}
        """
    )

else:
    st.warning("Kolom kategori soal tidak ditemukan.")

# =============================================================================
# 7️⃣ TABEL DATA
# =============================================================================
st.markdown(
    """
    <div style="padding:4px 12px; background-color:#f8f9fa; border-radius:15px; margin-bottom:15px">
        <h3>🏆 Top 10 Peserta Nilai Tertinggi</h3>
    </div>
    """,
    unsafe_allow_html=True
)

df_top10 = filtered.nlargest(10, "Nilai")[
    ["Nama", "Kelas", "SekolahNama", "SekolahKotaKabupaten", "Nilai"]
]

df_top10.index = range(1, len(df_top10) + 1)
df_top10.columns = ["Nama", "Kelas", "Sekolah", "Kota/Kab", "Nilai"]
st.dataframe(df_top10.style.format({"Nilai": "{:.2f}"}), use_container_width=True)

with st.expander("📋 Tampilkan Seluruh Data"):
    st.dataframe(
        filtered[["Nama", "Kelas", "SekolahNama", "SekolahKotaKabupaten", "Nilai"]],
        use_container_width=True
    )
