import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from streamlit_option_menu import option_menu

# Konfigurasi Halaman (Minimalist & Clean)
st.set_page_config(page_title="Dashboard Pendataan Ternak", layout="wide")

# Fungsi Load, Clean & Parse Data
@st.cache_data
def load_data():
    try:
        # Membaca format CSV baru
        df = pd.read_csv('Data Ternak Sarwodadi, Giritirta.xlsx - Sheet1.csv', header=None, skiprows=3)
    except:
        try:
            # Cadangan jika file bernama Excel
            df = pd.read_excel('Data Ternak Sarwodadi, Giritirta.xlsx', header=None, skiprows=3)
        except:
            st.error("File data tidak ditemukan. Pastikan nama filenya benar di GitHub.")
            return pd.DataFrame()
    
    # Memastikan hanya mengambil 17 kolom (mencegah error length mismatch)
    df = df.iloc[:, 0:17]
    
    df.columns = [
        'No', 'Nama Pemilik', 'RT', 'RW', 
        'Kambing_Jantan', 'Kambing_Betina', 'Kambing_Total', 'Kambing_Anakan',
        'Domba_Jantan', 'Domba_Betina', 'Domba_Total', 'Domba_Anakan',
        'Sapi_Jantan', 'Sapi_Betina', 'Sapi_Total', 'Sapi_Anakan',
        'Ketersediaan'
    ]
    
    # Fungsi khusus untuk menangani "0-" atau "-"
    def format_wilayah(val, prefix):
        if pd.isna(val):
            return "-"
        
        s = str(val).replace('.0', '').strip()
        # Jika isinya kosong, strip, atau nan, langsung kembalikan strip (tanpa 0)
        if s.lower() in ['nan', '-', '', 'none', '0-']:
            return "-"
            
        # Jika isinya murni angka tunggal (misal '1'), tambahkan 0 di depan
        if s.isdigit() and len(s) == 1:
            return f"{prefix} 0{s}"
            
        return f"{prefix} {s.upper()}"
    
    records = []
    for _, row in df.iterrows():
        # Lewati baris yang nama pemiliknya kosong
        if pd.isna(row['Nama Pemilik']):
            continue
            
        def parse_num(val):
            try:
                return float(val) if pd.notna(val) else 0.0
            except:
                return 0.0
                
        for jenis in ['Kambing', 'Domba', 'Sapi']:
            jantan = parse_num(row[f'{jenis}_Jantan'])
            betina = parse_num(row[f'{jenis}_Betina'])
            anakan = parse_num(row[f'{jenis}_Anakan'])
            
            # Hanya masukkan data jika warga memiliki jenis hewan tersebut
            if jantan > 0 or betina > 0 or anakan > 0:
                rt_rapi = format_wilayah(row['RT'], "RT")
                rw_rapi = format_wilayah(row['RW'], "RW")
                
                records.append({
                    'No': row['No'],
                    'Nama Pemilik': str(row['Nama Pemilik']).strip().title(),
                    'RT': rt_rapi,
                    'RW': rw_rapi,
                    'Jenis Ternak': jenis,
                    'Jantan': int(jantan),
                    'Betina': int(betina),
                    'Anakan': int(anakan),
                    'Total Ekor': int(jantan + betina + anakan),
                    'Ketersediaan': str(row['Ketersediaan']).strip() if pd.notna(row['Ketersediaan']) else 'Belum Konfirmasi'
                })
                
    final_df = pd.DataFrame(records)
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
    
    # Koordinat yang sudah digeser manual agar tepat di atas teks OpenStreetMap
    sarwodadi_coords = [-7.24700, 109.77150]
    giritirta_coords = [-7.24350, 109.78450]
    
    # Titik tengah kamera
    center_coords = [
        (sarwodadi_coords[0] + giritirta_coords[0]) / 2,
        (sarwodadi_coords[1] + giritirta_coords[1]) / 2
    ]
    
    m = folium.Map(location=center_coords, zoom_start=15)
    
    # Pin Desa Sarwodadi
    folium.Marker(
        location=sarwodadi_coords, 
        popup="Desa Sarwodadi", 
        tooltip="Desa Sarwodadi", 
        icon=folium.Icon(color="green", icon="leaf")
    ).add_to(m)
    
    # Pin Desa Giritirta
    folium.Marker(
        location=giritirta_coords, 
        popup="Desa Giritirta", 
        tooltip="Desa Giritirta", 
        icon=folium.Icon(color="darkgreen", icon="leaf")
    ).add_to(m)
    
    st_folium(m, width=700, height=400)

# ================= HALAMAN 2: DASHBOARD =================
elif menu == "📊 Dashboard Data Pertanian":
    st.title("📊 Dashboard Pendataan Peternak Warga")
    st.write("---")

    st.sidebar.header("🔎 Filter Data")
    if not data_peternak.empty:
        filter_mode = st.sidebar.radio("Filter berdasarkan:", ["RW", "RT"])

        # Memastikan opsi filter '-' (data kosong) tidak perlu dipilih secara default
        if filter_mode == "RW":
            pilihan_unik = sorted([x for x in data_peternak["RW"].unique() if x != "-"])
            selected_lokasi = st.sidebar.multiselect("Pilih RW", options=pilihan_unik, default=pilihan_unik)
            filtered_data = data_peternak[data_peternak["RW"].isin(selected_lokasi)]
        else:
            pilihan_unik = sorted([x for x in data_peternak["RT"].unique() if x != "-"])
            selected_lokasi = st.sidebar.multiselect("Pilih RT", options=pilihan_unik, default=pilihan_unik)
            filtered_data = data_peternak[data_peternak["RT"].isin(selected_lokasi)]

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

        st.subheader("📄 Data Peternak")
        tabel_tampil = filtered_data[['Nama Pemilik', 'RT', 'RW', 'Jenis Ternak', 'Jantan', 'Betina', 'Anakan', 'Total Ekor', 'Ketersediaan']]
        st.dataframe(tabel_tampil, use_container_width=True)
        st.write("---")

        st.subheader("📊 Total Ternak per RT")
        total_per_rt = filtered_data.groupby(["RT", "Jenis Ternak"])["Total Ekor"].sum().reset_index()
        fig_rt = px.bar(
            total_per_rt, x="RT", y="Total Ekor", color="Jenis Ternak",
            barmode="group", color_discrete_sequence=earth_tones, text_auto=True
        )
        fig_rt.update_xaxes(type='category', title_text='Rukun Tetangga (RT)')
        st.plotly_chart(fig_rt, use_container_width=True)

        st.subheader("🏘️ Total Ternak per RW")
        total_per_rw = filtered_data.groupby(["RW", "Jenis Ternak"])["Total Ekor"].sum().reset_index()
        fig_rw = px.bar(
            total_per_rw, x="RW", y="Total Ekor", color="Jenis Ternak",
            barmode="group", color_discrete_sequence=earth_tones, text_auto=True
        )
        fig_rw.update_xaxes(type='category', title_text='Rukun Warga (RW)')
        st.plotly_chart(fig_rw, use_container_width=True)

        st.subheader("🥧 Distribusi Ternak Keseluruhan")
        total_all = filtered_data.groupby("Jenis Ternak")["Total Ekor"].sum().reset_index()
        fig_pie = px.pie(
            total_all, names="Jenis Ternak", values="Total Ekor",
            color_discrete_sequence=earth_tones
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Data belum tersedia atau gagal dimuat.")
