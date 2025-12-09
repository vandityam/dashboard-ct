import streamlit as st
import pandas as pd
import plotly.express as px

# =============================================================================
# KONFIGURASI DASHBOARD
# =============================================================================
st.set_page_config(page_title="Dashboard Bebras Challenge", layout="wide")

# =============================================================================
# LOAD CSS
# =============================================================================
def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# =============================================================================
# JUDUL DASHBOARD
# =============================================================================
st.markdown("<h1 class='main-title'>Dashboard Hasil Bebras Challenge 2024</h1>", unsafe_allow_html=True)
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
# MAPPING (UNTUK FILTER CASCADING)
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
st.sidebar.markdown("<div class='sidebar-title'>🔍 Filter Data</div>", unsafe_allow_html=True)

provinsi = st.sidebar.multiselect("Pilih Provinsi:", sorted(bebras["Provinsi"].dropna().unique()))
if provinsi:
    kota_allowed = sorted({k for p in provinsi for k in mapping_prov_kota.get(p, [])})
else:
    kota_allowed = sorted(bebras["SekolahKotaKabupaten"].dropna().unique())

kota = st.sidebar.multiselect("Pilih Kota/Kabupaten:", kota_allowed)

kategori = st.sidebar.multiselect("Pilih Kategori:", sorted(bebras["Kategori"].dropna().unique()))
if kategori:
    kelas_allowed = sorted({k for cat in kategori for k in mapping_kategori_kelas.get(cat, [])})
else:
    kelas_allowed = sorted(bebras["Kelas"].dropna().unique())

kelas = st.sidebar.multiselect("Pilih Kelas:", kelas_allowed)

# Filter data
filtered = bebras.copy()
if provinsi: filtered = filtered[filtered["Provinsi"].isin(provinsi)]
if kota: filtered = filtered[filtered["SekolahKotaKabupaten"].isin(kota)]
if kategori: filtered = filtered[filtered["Kategori"].isin(kategori)]
if kelas: filtered = filtered[filtered["Kelas"].isin(kelas)]

st.sidebar.markdown(f"<p class='small-info'>Total data: <b>{len(filtered)} peserta</b></p>", unsafe_allow_html=True)

# =============================================================================
# INFORMASI FILTER AKTIF
# =============================================================================
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
st.markdown("<div class='section-title'>📊 Statistik Ringkas</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Jumlah Peserta", len(filtered))
col2.metric("Rata-rata Nilai", round(filtered["Nilai"].mean(), 2))
col3.metric("Nilai Tertinggi", round(filtered["Nilai"].max(), 2))
col4.metric("Nilai Terendah", round(filtered["Nilai"].min(), 2))
# =============================================================================
# 2️⃣ DEMOGRAFI PESERTA
# =============================================================================
st.markdown("<div class='section-title'>👥 Demografi Peserta</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    gender_counts = filtered["JenisKelamin"].value_counts().reset_index()
    gender_counts.columns = ["JenisKelamin", "Jumlah"]

    fig_gender = px.pie(
        gender_counts,
        values="Jumlah",
        names="JenisKelamin",
        title="Distribusi Jenis Kelamin"
    )

    fig_gender.update_layout(
        height=250,   
        width=250,    
        margin=dict(l=20, r=20, t=30, b=20),
    )

    st.plotly_chart(fig_gender, use_container_width=True)

with col2:
    kelas_counts = filtered["Kelas"].value_counts().reset_index()
    kelas_counts.columns = ["Kelas", "Jumlah"]

    fig_kelas = px.bar(
        kelas_counts,
        x="Kelas",
        y="Jumlah",
        title="Distribusi Kelas"
    )

    fig_kelas.update_layout(
        height=250,   
        width=250,    
        margin=dict(l=10, r=10, t=40, b=10),
    )

    st.plotly_chart(fig_kelas, use_container_width=True)


# =============================================================================
# 3️⃣ DISTRIBUSI WILAYAH
# =============================================================================
st.markdown("<div class='section-title'>🌍 Distribusi Wilayah Peserta</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    prov_counts = filtered["Provinsi"].value_counts().reset_index()
    prov_counts.columns = ["Provinsi", "Jumlah"]

    fig_prov = px.bar(
        prov_counts,
        x="Jumlah",
        y="Provinsi",
        orientation="h",
        title="Peserta per Provinsi"
    )

    fig_prov.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_prov, use_container_width=True)

with col2:
    kota_counts = filtered["SekolahKotaKabupaten"].value_counts().reset_index()
    kota_counts.columns = ["Kota/Kabupaten", "Jumlah"]

    fig_kota = px.bar(
        kota_counts,
        x="Jumlah",
        y="Kota/Kabupaten",
        orientation="h",
        title="Peserta per Kota/Kabupaten"
    )

    fig_kota.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_kota, use_container_width=True)


# =============================================================================
# 4️⃣ ANALISIS NILAI
# =============================================================================
st.markdown("<div class='section-title'>🎯 Analisis Nilai Peserta</div>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    fig_hist = px.histogram(filtered, x="Nilai", nbins=10, title="Histogram Nilai")
    fig_hist.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    fig_box = px.box(filtered, y="Nilai", title="Boxplot Nilai")
    fig_box.update_layout(
        height=280,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_box, use_container_width=True)


# Rata-rata per kategori
df_avg_kat = filtered.groupby("Kategori", as_index=False)["Nilai"].mean().sort_values("Nilai", ascending=False)

fig_kat_score = px.bar(
    df_avg_kat,
    x="Kategori",
    y="Nilai",
    title="Rata-rata Nilai per Kategori"
)

fig_kat_score.update_layout(
    height=300,
    margin=dict(l=10, r=10, t=40, b=10)
)

st.plotly_chart(fig_kat_score, use_container_width=True)


# =============================================================================
# 5️⃣ PERFORMA SEKOLAH
# =============================================================================
st.markdown("<div class='section-title'>🏫 Performa Sekolah</div>", unsafe_allow_html=True)

top_n = st.slider("Tampilkan Top-N Sekolah:", 5, 30, 10)
df_school = filtered.groupby("SekolahNama")["Nilai"].mean().reset_index().sort_values("Nilai", ascending=False)

fig_school = px.bar(
    df_school.head(top_n),
    x="Nilai",
    y="SekolahNama",
    orientation="h",
    title=f"Top {top_n} Sekolah Berdasarkan Nilai"
)

fig_school.update_layout(
    height=350,
    margin=dict(l=10, r=10, t=40, b=10)
)

st.plotly_chart(fig_school, use_container_width=True)


# =============================================================================
# 6️⃣ ANALISIS KATEGORI SOAL
# =============================================================================
st.markdown("<div class='section-title'>🧩 Analisis Kategori Soal</div>", unsafe_allow_html=True)

kategori_cols = [c for c in filtered.columns if c.startswith("S ") or c.startswith("S_")]

if kategori_cols:
    df_kat = filtered[kategori_cols].mean().reset_index()
    df_kat.columns = ["Kategori", "RataRata"]

    fig_kat = px.bar(df_kat, x="Kategori", y="RataRata", title="Rata-rata Nilai Kategori Soal")

    fig_kat.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=40, b=10)
    )

    st.plotly_chart(fig_kat, use_container_width=True)

    # summary insight
    best = df_kat.nlargest(1, "RataRata").iloc[0]
    worst = df_kat.nsmallest(1, "RataRata").iloc[0]

    st.success(
        f"**Kekuatan terbesar:** {best['Kategori']} (rata-rata {best['RataRata']:.2f})\n\n"
        f"**Kelemahan terbesar:** {worst['Kategori']} (rata-rata {worst['RataRata']:.2f})"
    )

else:
    st.warning("Kolom kategori soal tidak ditemukan.")

# =============================================================================
# 7️⃣ TABEL DATA
# =============================================================================
st.markdown("<div class='section-title'>📋 Data Peserta Nilai Tertinggi</div>", unsafe_allow_html=True)

df_top10 = filtered.nlargest(10, "Nilai")[["Nama", "Kelas", "SekolahNama", "SekolahKotaKabupaten", "Nilai"]]
df_top10.index = range(1, len(df_top10) + 1)
df_top10.columns = ["Nama", "Kelas", "Sekolah", "Kota/Kab", "Nilai"]

st.dataframe(df_top10.style.format({"Nilai": "{:.2f}"}), use_container_width=True)

with st.expander("Tampilkan Seluruh Data"):
    st.dataframe(filtered[["Nama", "Kelas", "SekolahNama", "SekolahKotaKabupaten", "Nilai"]],
                 use_container_width=True)
