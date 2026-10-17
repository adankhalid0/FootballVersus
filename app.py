
import base64
from pathlib import Path

import requests
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(
    page_title="FootballVersus",
    page_icon="⚽",
    layout="wide"
)

# ==========================================
# SPILLERE OG SESONG
# ==========================================

SESONG = 2023

SPILLERE = {
    "Vinícius Júnior": {
        "id": 762,
        "team": 541,
        "klubb": "Real Madrid",
        "liga": 140,
        "sok": "Vinicius"
    },
    "Kylian Mbappé": {
        "id": 278,
        "team": 85,
        "klubb": "Paris Saint-Germain",
        "liga": 61,
        "sok": "Mbappe"
    },
    "Jude Bellingham": {
        "id": None,
        "team": 541,
        "klubb": "Real Madrid",
        "liga": 140,
        "sok": "Bellingham"
    },
    "Lamine Yamal": {
        "id": 386828,
        "team": 529,
        "klubb": "Barcelona",
        "liga": 140,
        "sok": "Yamal"
    },
    "Erling Haaland": {
        "id": None,
        "team": 50,
        "klubb": "Manchester City",
        "liga": 39,
        "sok": "Haaland"
    },
    "Pedri": {
        "id": None,
        "team": 529,
        "klubb": "Barcelona",
        "liga": 140,
        "sok": "Pedri"
    }
}

REAL_MADRID = [
    "Vinícius Júnior",
    "Kylian Mbappé",
    "Jude Bellingham"
]

MOTSTANDERE = [
    "Lamine Yamal",
    "Erling Haaland",
    "Pedri"
]

# ==========================================
# DESIGN OG STADIONBAKGRUNN
# ==========================================

st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(
            circle at 15% 10%,
            #233d75,
            transparent 45%
        ),
        radial-gradient(
            circle at 90% 20%,
            #47234f,
            transparent 45%
        ),
        #080e20;
    color: white;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
}

.hero {
    text-align: center;
    padding: 35px 20px;
    border: 1px solid #536ca2;
    border-radius: 24px;
    background: linear-gradient(
        120deg,
        rgba(32, 54, 101, 0.93),
        rgba(23, 29, 57, 0.93),
        rgba(66, 35, 78, 0.93)
    );
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 3rem;
    color: #f5d477;
}

.player-card {
    background: rgba(23, 34, 64, 0.94);
    border: 1px solid #52699a;
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    min-height: 145px;
}

.player-card h2 {
    color: white;
}

.player-card p {
    color: #f5d477;
}

.vs {
    text-align: center;
    font-size: 3rem;
    font-weight: bold;
    color: #f5d477;
    padding-top: 60px;
}
</style>
""", unsafe_allow_html=True)

# Hvis assets/bernabeu.jpg finnes,
# brukes bildet som bakgrunn.

stadionfil = (
    Path(__file__).parent
    / "assets"
    / "bernabeu.jpg"
)

if stadionfil.exists():
    bilde64 = base64.b64encode(
        stadionfil.read_bytes()
    ).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(
                    rgba(5, 10, 28, 0.82),
                    rgba(5, 10, 28, 0.91)
                ),
                url("data:image/jpeg;base64,{bilde64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# API-FOOTBALL
# ==========================================

API_URL = "https://v3.football.api-sports.io"


@st.cache_data(ttl=3600)
def api_kall(endepunkt, parametere):
    headers = {
        "x-apisports-key":
            st.secrets["API_FOOTBALL_KEY"]
    }

    svar = requests.get(
        f"{API_URL}/{endepunkt}",
        headers=headers,
        params=parametere,
        timeout=15
    )

    svar.raise_for_status()

    data = svar.json()

    if data.get("errors"):
        raise ValueError(str(data["errors"]))

    return data.get("response", [])


@st.cache_data(ttl=3600)
def finn_spiller_id(spillernavn):
    info = SPILLERE[spillernavn]

    if info["id"] is not None:
        return info["id"]

    resultater = api_kall(
        "players",
        {
            "search": info["sok"],
            "team": info["team"],
            "season": SESONG
        }
    )

    for resultat in resultater:
        spiller = resultat.get("player", {})
        navn = spiller.get("name", "").lower()

        # Velg en spiller med riktig etternavn.
        etternavn = info["sok"].lower()

        if etternavn in navn:
            return spiller.get("id")

    return None


@st.cache_data(ttl=3600)
def hent_statistikk(spillernavn):
    info = SPILLERE[spillernavn]
    spiller_id = finn_spiller_id(spillernavn)

    if spiller_id is None:
        return None

    resultater = api_kall(
        "players",
        {
            "id": spiller_id,
            "team": info["team"],
            "season": SESONG
        }
    )

    for resultat in resultater:
        for stats in resultat.get(
            "statistics", []
        ):
            liga = stats.get("league", {})

            if (
    liga.get("id") == info["liga"]
    and liga.get("season") == SESONG
):
                kamper = stats.get("games", {})
                maal = stats.get("goals", {})

                return {
                    "Kamper":
                        kamper.get("appearences") or 0,
                    "Minutter":
                        kamper.get("minutes") or 0,
                    "Mål":
                        maal.get("total") or 0,
                    "Assists":
                        maal.get("assists") or 0,
                    "Bilde":
                        resultat.get(
                            "player", {}
                        ).get("photo"),
                    "Logo":
                        stats.get(
                            "team", {}
                        ).get("logo"),
                    "Liga":
                        liga.get("name", ""),
                    "Klubb":
                        info["klubb"]
                }

    return None


# ==========================================
# OVERSKRIFT
# ==========================================

st.markdown("""
<div class="hero">
    <h1>⚽ FootballVersus</h1>
    <h3>
        Real Madrid møter resten
        av fotballverdenen
    </h3>
    <p>
        🏆 Sammenlign fotballstjerner
        med ekte statistikk
    </p>
</div>
""", unsafe_allow_html=True)

st.info(
    "📊 API-Football | Sesong 2023/24 | "
    "Ligastatistikk"
)

# ==========================================
# VELG SPILLERE
# ==========================================

col1, col2 = st.columns(2)

with col1:
    spiller1 = st.selectbox(
        "Velg Real Madrid-spiller",
        REAL_MADRID
    )

with col2:
    spiller2 = st.selectbox(
        "Velg motstander",
        MOTSTANDERE
    )

# ==========================================
# HENT STATISTIKK
# ==========================================

try:
    with st.spinner(
        "Henter ekte spillerstatistikk..."
    ):
        data1 = hent_statistikk(spiller1)
        data2 = hent_statistikk(spiller2)

except (
    requests.RequestException,
    ValueError,
    KeyError
) as feil:
    st.error(
        f"Kunne ikke hente API-data: {feil}"
    )
    st.stop()

if data1 is None or data2 is None:
    st.warning(
        "Fant ikke statistikk for én eller "
        "begge spillerne. Kontroller at "
        "API-et har data for sesongen."
    )
    st.stop()

# ==========================================
# SPILLERKORT
# ==========================================

venstre, midten, hoyre = st.columns(
    [5, 1, 5]
)

with venstre:
    if data1["Bilde"]:
        st.image(
            data1["Bilde"],
            width=180
        )

    if data1["Logo"]:
        st.image(
            data1["Logo"],
            width=55
        )

    st.markdown(
        f"""
        <div class="player-card">
            <h2>{spiller1}</h2>
            <p>{data1["Klubb"]}</p>
            <p>{data1["Liga"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with midten:
    st.markdown(
        '<div class="vs">VS</div>',
        unsafe_allow_html=True
    )

with hoyre:
    if data2["Bilde"]:
        st.image(
            data2["Bilde"],
            width=180
        )

    if data2["Logo"]:
        st.image(
            data2["Logo"],
            width=55
        )

    st.markdown(
        f"""
        <div class="player-card">
            <h2>{spiller2}</h2>
            <p>{data2["Klubb"]}</p>
            <p>{data2["Liga"]}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# STATISTIKKTABELL
# ==========================================

st.markdown("## 📊 Spillerstatistikk")

statistikk = pd.DataFrame({
    spiller1: {
        "Kamper": data1["Kamper"],
        "Minutter": data1["Minutter"],
        "Mål": data1["Mål"],
        "Assists": data1["Assists"]
    },
    spiller2: {
        "Kamper": data2["Kamper"],
        "Minutter": data2["Minutter"],
        "Mål": data2["Mål"],
        "Assists": data2["Assists"]
    }
})

st.dataframe(
    statistikk,
    use_container_width=True
)

# ==========================================
# SAMMENLIGNINGSDIAGRAM
# ==========================================

st.markdown("## 📈 Sammenligning")

diagramdata = (
    statistikk
    .loc[["Mål", "Assists"]]
    .rename_axis("Statistikk")
    .reset_index()
    .melt(
        id_vars="Statistikk",
        var_name="Spiller",
        value_name="Antall"
    )
)

diagram = (
    alt.Chart(diagramdata)
    .mark_bar()
    .encode(
        x=alt.X(
            "Statistikk:N",
            title=None
        ),
        xOffset="Spiller:N",
        y=alt.Y(
            "Antall:Q",
            title="Antall"
        ),
        color=alt.Color(
            "Spiller:N",
            scale=alt.Scale(
                domain=[spiller1, spiller2],
                range=["#3197ff", "#f5d477"]
            )
        ),
        tooltip=[
            "Spiller",
            "Statistikk",
            "Antall"
        ]
    )
    .properties(height=350)
)

st.altair_chart(
    diagram,
    use_container_width=True
)

# ==========================================
# OPPSUMMERING
# ==========================================

st.markdown("## 🏆 Hvem scoret flest mål?")

if data1["Mål"] > data2["Mål"]:
    st.success(
        f"⚽ {spiller1} scoret flest mål!"
    )
elif data2["Mål"] > data1["Mål"]:
    st.success(
        f"⚽ {spiller2} scoret flest mål!"
    )
else:
    st.info(
        "Spillerne scoret like mange mål!"
    )

st.caption(
    "FootballVersus | API-Football | "
    "Ligastatistikk 2023/24. "
    "Spillernes klubber vises slik de var "
    "i den valgte sesongen."
)
