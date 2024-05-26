import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

data = pd.read_csv("../export.csv")
data = data[data["vax_kat"] != 1]
data["vax_kat"] = data["vax_kat"].astype(str)

born_options = data["born"].unique()


def vax_mapping(vax_kat: str) -> str:
    assert isinstance(vax_kat, str)
    if int(vax_kat[0]) == 0:
        return "Unvax"
    elif int(vax_kat[0]) == 1:
        return "Dose 1"
    elif int(vax_kat[0]) == 2:
        return "Dose 2"
    elif int(vax_kat[0]) >= 3:
        return "Dose 3+"
    else:
        raise ValueError(f"Unknown vax_kat: {vax_kat}")


COLOR_MAPPING = {
    "Unvax": "red",
    "Dose 1": "blue",
    "Dose 2": "green",
    "Dose 3+": "purple",
}


data["group"] = data["vax_kat"].apply(vax_mapping)


st.title("UZIS Vax Visual")

born_option = st.selectbox(
    "Rok",
    born_options,
    index=0,
    placeholder="Select group...",
)


df = data[data["born"] == born_option]


df["chart1"] = df["no_of_persondays"] / 365.25
df["chart2"] = df["no_of_dead"] / (1e3 * df["no_of_persondays"] * 365.25)
df["chart3"] = df["no_of_dead"] / (1e3 * df["no_of_persondays"] * 365.25)


xx = df["month"].values

value1 = df["no_of_persondays"].values / 365.25

# print(xx)
# print(value1)

assert len(xx) == len(value1)

colors = px.colors.qualitative.Vivid

fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.02)


# fig1 = px.bar(df, x="month", y="chart1", color="group", barmode="stack", color_discrete_sequence=colors)
# fig2 = px.bar(df, x="month", y="chart2", color="group", color_discrete_sequence=colors)
# fig3 = px.bar(df, x="month", y="chart3", color="group", color_discrete_sequence=colors)
#
# st.plotly_chart(fig1, theme="streamlit", use_container_width=True)
# st.plotly_chart(fig2, theme="streamlit", use_container_width=True)
# st.plotly_chart(fig3, theme="streamlit", use_container_width=True)

# Graf 1. Na ose X month. Na ose Y no_of_persondays / 365.25. Segmentováno dle vax_kat. Ale vax_kat musela být nějak pogrupovaná – asi podle první číslice kódu?
# Graf 2. To samé co Graf 1 až na následující změny. Na ose Y je no_of_dead / (1e3 * no_of_persondays / 365.25).
# Graf 3. To samé co Graf 1 až na následující změny. Na ose Y je no_of_dead[vax_kat] / no_of_dead[unvax].
# Na Grafu 3 bych přepočítal osu Y na 1 – no_of_dead[vax_kat] / no_of_dead[unvax], aby střed byl v nule a lépe se to srovnávalo. Vyhodil bych také křivku pro no_of_dead[unvax] / no_of_dead[unvax], která je vždy 1.

fig.add_traces(
    [
        go.Bar(
            x=dd["month"],
            y=dd["no_of_persondays"] / 365.25,
            name=name,
            legendgroup=name,
            marker=go.bar.Marker(color=COLOR_MAPPING[name]),
            # offsetgroup=1,
        )
        for k, (name, dd) in enumerate(df.groupby("group"))
    ],
    rows=1,
    cols=1,
)

fig.add_traces(
    [
        go.Bar(
            x=dd["month"],
            y=dd["no_of_dead"] / (1e3 * dd["no_of_persondays"] * 365.25),
            name=name,
            legendgroup=name,
            showlegend=False,
            marker=go.bar.Marker(color=COLOR_MAPPING[name]),
        )
        for name, dd in df.groupby("group")
    ],
    rows=2,
    cols=1,
)


fig.add_traces(
    [
        go.Bar(
            x=dd["month"],
            y=1 - dd["no_of_dead"] / df.loc[df["group"] == "Unvax", "no_of_dead"],
            name=name,
            legendgroup=name,
            showlegend=False,
            marker=go.bar.Marker(color=COLOR_MAPPING[name]),
        )
        for name, dd in df.groupby("group")
    ],
    rows=3,
    cols=1,
)


fig.update_layout(
    height=600,
    width=600,
    title_text="Stacked Subplots with Shared X-Axes",
    # barmode="stack",
    barmode="group",
    coloraxis=dict(colorscale="RdBu"),
)

st.plotly_chart(fig, theme="streamlit", use_container_width=True)

data[data["born"] == born_option]
