import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Konfigurasi Halaman (Minimalist & Clean)
st.set_page_config(page_title="Dashboard Pendataan Ternak", layout="wide")

# Fungsi Load, Clean & PIVOT Data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('Data Ternak Sarwodadi, Giritirta.xlsx', sheet_name='SARWODADI', header=1)
    except:
        df = pd.read_csv('Data Ternak Sarwodadi, Giritirta.xlsx - SARWODADI.csv', header=1)
    
    # 1. Ambil kolom mentah
    df_s = df.iloc[:, 0:10].copy()
    df_s.columns = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jenis kelamin', 'Jumlah Dewasa', 'Total', 'Ketersediaan', 'Anakan']
    
    # 2. Forward fill identitas
    kolom_identitas = ['No', 'Nama Pemilik', 'RT', 'RW', 'Jenis Ternak']
    df_s[kolom_identitas] = df_s[kolom_identitas].ffill()
    
    # 3. Merapikan string RT dan RW
    df_s['RT_str'] = "RT 0" + df_s['RT'].astype(str).str.replace('.0', '', regex=False)
    df_s['RW_str'] = "RW 0" + df_s['RW'].astype(str).str.replace('.0', '', regex=False)
    
    # 4. Memastikan angka benar-benar angka (kosong = 0)
    df_s['Jumlah Dewasa'] = pd.to_numeric(df_s['Jumlah Dewasa'], errors='coerce').fillna(0)
    df_s['Anakan'] = pd.to_numeric(df_s['Anakan'], errors='coerce').fillna(0)
    
    # 5. Menangani Ketersediaan (Forward fill khusus untuk orang yang sama, lalu sisa kosong diisi Belum Konfirmasi)
    df_s['Ketersediaan'] = df_s.groupby('Nama Pemilik')['Ketersediaan'].ffill().fillna('Belum Konfirmasi')
    
    # Membuang baris yang tidak ada isinya
    df_s = df_s[df_s['Jenis kelamin'].notna() | (df_s['Jumlah Dewasa'] > 0) | (df_s['Anakan'] > 0)]
    
    # 6. PIVOT TABLE: Menggeser Jantan & Betina menjadi kolom (ke samping)
    pivot_df = df_s.pivot_table(
        index=['No', 'Nama Pemilik', 'RT_str', 'RW_str', 'Jenis Ternak'],
        columns='Jenis kelamin',
        values='Jumlah Dewasa',
        aggfunc='sum'
    ).reset_index()
    
    # 7. AGREGASI: Menjumlahkan Anakan dan mengambil Ketersediaan
    agg_df = df_s.groupby(['No', 'Nama Pemilik', 'RT_str', 'RW_str', 'Jenis Ternak']).agg({
        'Anakan': 'sum',
        'Ketersediaan': 'first' # Mengambil status persetujuan peternak
    }).reset_index()
    
    # 8. GABUNGKAN DATA
    final_df = pd.merge(pivot_df, agg_df, on=['No', 'Nama Pemilik', 'RT_str', 'RW_str', 'Jenis Ternak'])
    
    # Memastikan kolom Jantan & Betina selalu ada meskipun datanya kosong
    if 'Jantan' not in final_df.columns: final_df['Jantan'] = 0
    if 'Betina' not in final_df.columns: final_df['Betina'] = 0
    
    final_df = final_df.fillna(0) # Mengubah NaN di kolom jantan/betina menjadi 0
    final_df.rename(columns={'RT_str': 'RT', 'RW_str': 'RW'}, inplace=True)
    
    # 9. Menghitung Total Ekor per individu
    final_df['Total Ekor'] = final_df['Jantan'] + final_df['Betina'] + final_df['Anakan']
    
    # Urutkan berdasarkan Nomor asli agar rapi
    final_df = final_df.sort_values('No').reset_index(drop=True)
    
    return final_df

data_peternak = load_data()
earth_tones = ['#8D6E63', '#D7CCC8', '#A1887F', '#5D4037', '#BCAAA4']

# Sidebar Navigasi
with st.sidebar:
    menu = option_menu(
        "📌 Menu Navigasi",
        ["📖 Profil Desa", "📊 Dashboard Data Pertanian"],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "#5D4037", "font-size": "20px"}, 
            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#8D6E63"},
        }
    )

# ================= HALAMAN 1: PROFIL DESA =================
if menu == "📖 Profil Desa":
    st.markdown("## 📖 Profil Desa Sarwodadi & Giritirta")
    st.write("---")
    st.markdown("""
    **Desa Sarwodadi dan Desa Giritirta** adalah dua wilayah yang bertetangga dan saling bersinergi di utara Kabupaten Banjarnegara. 
    Dikelilingi oleh keasrian alam khas pegunungan, kedua desa ini memiliki lingkungan yang sangat mendukung kemajuan sektor agraris.
    
    ### 👥 Potensi Peternakan Warga
    Warga di Desa Sarwodadi dan Giritirta sangat proaktif dalam memanfaatkan potensi alamnya, salah satunya melalui sektor peternakan yang menjadi pundi-pundi ekonomi keluarga.
    
    Berdasarkan hasil pendataan wilayah terkini, hewan ternak yang menjadi komoditas utama warga di kedua desa ini meliputi:
    * **Kambing**
    * **Domba**
    * **Sapi**
    """)

    st.markdown("### 🗺️ Peta Wilayah")
    desa_coords = [-7.2472, 109.8111] 
    m = folium.Map(location=desa_coords, zoom_start=13)
    folium.Marker(
        location=desa_coords, popup="Desa Sarwodadi & Giritirta", tooltip="Lokasi", icon=folium.Icon(color="darkgreen", icon="leaf")
    ).add_to(m)
    st_folium(m, width=700, height=400)

# ================= HALAMAN 2: DASHBOARD =================
elif menu == "📊 Dashboard Data Pertanian":
    st.title("📊 Dashboard Pendataan Peternak Warga")
    st.write("---")

    # === Sidebar Filter ===
    st.sidebar.header("🔎 Filter Data")
    filter_mode = st.sidebar.radio("Filter berdasarkan:", ["RW", "RT"])

    if filter_mode == "RW":
        pilihan_unik = sorted(data_peternak["RW"].unique())
        selected_lokasi = st.sidebar.multiselect("Pilih RW", options=pilihan_unik, default=pilihan_unik)
        filtered_data = data_peternak[data_peternak["RW"].isin(selected_lokasi)]
    else:
        pilihan_unik = sorted(data_peternak["RT"].unique())
        selected_lokasi = st.sidebar.multiselect("Pilih RT", options=pilihan_unik, default=pilihan_unik)
        filtered_data = data_peternak[data_peternak["RT"].isin(selected_lokasi)]

    # === Metrik Angka Utama ===
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Populasi Ternak", value=f"{int(filtered_data['Total Ekor'].sum())} Ekor")
    with col2:
        st.metric(label="Total Peternak", value=f"{filtered_data['Nama Pemilik'].nunique()} Orang")
    with col3:
        if not filtered_data.empty:
            st.metric(label="Jenis Ternak Terbanyak", value=filtered_data.groupby('Jenis Ternak')['Total Ekor'].sum().idxmax())
        else:
            st.metric(label="Jenis Ternak Terbanyak", value="-")

    st.write("---")

    # === Dataframe Rapi (Seperti Foto) ===
    st.subheader("📄 Data Peternak")
    # Memilih kolom yang akan ditampilkan agar rapi memanjang ke samping
    tabel_tampil = filtered_data[['Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jantan', 'Betina', 'Anakan', 'Total Ekor', 'Ketersediaan']]
    
    # Menghilangkan angka desimal di tabel
    tabel_tampil = tabel_tampil.copy()
    for col in ['Jantan', 'Betina', 'Anakan', 'Total Ekor']:
        tabel_tampil[col] = tabel_tampil[col].astype(int)
        
    st.dataframe(tabel_tampil, use_container_width=True)
    st.write("---")

    # === Bar chart per RT ===
    st.subheader("📊 Total Ternak per RT")
    total_per_rt = filtered_data.groupby(["RT", "Jenis Ternak"])["Total Ekor"].sum().reset_index()
    fig_rt = px.bar(
        total_per_rt, x="RT", y="Total Ekor", color="Jenis Ternak",
        barmode="group", color_discrete_sequence=earth_tones, text_auto=True
    )
    fig_rt.update_xaxes(type='category', title_text='Rukun Tetangga (RT)')
    st.plotly_chart(fig_rt, use_container_width=True)

    # === Bar chart per RW ===
    st.subheader("🏘️ Total Ternak per RW")
    total_per_rw = filtered_data.groupby(["RW", "Jenis Ternak"])["Total Ekor"].sum().reset_index()
    fig_rw = px.bar(
        total_per_rw, x="RW", y="Total Ekor", color="Jenis Ternak",
        barmode="group", color_discrete_sequence=earth_tones, text_auto=True
    )
    fig_rw.update_xaxes(type='category', title_text='Rukun Warga (RW)')
    st.plotly_chart(fig_rw, use_container_width=True)

    # === Pie chart total ===
    st.subheader("🥧 Distribusi Ternak Keseluruhan")
    total_all = filtered_data.groupby("Jenis Ternak")["Total Ekor"].sum().reset_index()
    fig_pie = px.pie(
        total_all, names="Jenis Ternak", values="Total Ekor",
        color_discrete_sequence=earth_tones
    )
    st.plotly_chart(fig_pie, use_container_width=True)
