import streamlit as st
import dhlab_v2 as d2
import pandas as pd
from PIL import Image
import urllib

@st.cache(suppress_st_warning=True, show_spinner = False)
def sumword(NGRAM, words = None, ddk = None, topic = None, period = None, lang = None, title = None):
    wordlist =   [x.strip() for x in words.split(',')]
    # check if trailing comma, or comma in succession, if so count comma in
    if '' in wordlist:
        wordlist = [','] + [y for y in wordlist if y != '']
    ref = NGRAM(wordlist, ddk = ddk, topic = topic, period = period, lang = lang, title = title).sum(axis = 1)
    ref.columns = 'tot'
    return ref


@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(NGRAM, word = None, ddk = None, subject = None, period = None, lang = None, title = None):
    res = NGRAM(word, ddk = ddk, topic = subject, period = period, lang = lang, title = title)
    res = res.rolling(window = smooth_slider).mean()
    res.index = pd.to_datetime(res.index, format='%Y')
    return res

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.markdown('Les mer om DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb)')


st.title('Ord og bigram')
st.markdown('### bare enkeltord for øyeblikket')

st.markdown('### Trendlinjer')

st.sidebar.header('Input')
words = st.text_input('Fyll inn ord eller bigram adskilt med komma. Det skilles mellom store og små bokstaver', "rakørret, gravlaks")

allword = list(set([w.strip() for w in words.split(',')]))[:30]

lang = st.sidebar.selectbox('Målform', ['nob', 'nno', 'sme'], index = 0)

sammenlign = st.sidebar.text_input("Sammenling med summen av følgende ord - sum av komma og punktum er standard", ".,")
 


st.sidebar.header('Litt metadata')
texts = st.sidebar.selectbox('Bok eller tidsskrift', ['bok', 'tidsskrift'], index=0)

if texts == "bok":
    NGRAM = d2.ngram_book
    doctype = "digibok"
else:
    NGRAM = d2.ngram_periodicals
    doctype = "digitidsskrift"

    
st.sidebar.subheader('Tittel')
title = st.sidebar.text_input("Angi en del eller hele tittelen på boka eller tidsskriftet", "")
if title == "":
    title = None
    title_ft = None
else:
    title = "%" + "%".join(title.split()) + "%" 
    title_ft = title.replace("%", " ")
    #st.write(title.split())
    
st.sidebar.subheader('Dewey')
st.sidebar.markdown("Se definisjoner av [Deweys desimalkoder](https://deweysearchno.pansoft.de/webdeweysearch/index.html).")


ddki = st.sidebar.text_input('Skriv bare de første sifrene, for eksempel 8 for alle nummer som starter med 8, som gir treff på all kodet skjønnlitteratur.', "")

ddk_ft = None
ddk = None

if ddki == "":
    ddki = None

if ddki != None and not ddki.endswith("%"):
    ddk = ddki + "%"
    ddk_ft = (ddki + "*").replace('.', '"."')

st.sidebar.subheader('Temaord')


subject_ft = None
subject = st.sidebar.text_input('Temaord fra Nasjonalbibliografien - Marc21 felt 653', '')
if subject == '':
    subject = None
elif not "%" in subject:
    subject = "%" + subject.strip() + "%"
    subject_ft = subject.replace('%', '')

st.sidebar.subheader('Tidsperiode')

period_slider = st.sidebar.slider(
    'Angi periode i år',
    1700, 2023, (1950, 2018)
)

# wrapper for nb.frame() check if dataframe is empty before assigning names to columns
def frm(x, y):
    if not x.empty:
        res = pd.DataFrame(x, columns = [y])
    else:
        res = x
    return res

st.sidebar.header('Visning')
smooth_slider = st.sidebar.slider('Glatting', 1, 8, 3)


try:
    df = ngram(NGRAM, allword, ddk = ddk, subject = subject, period = (period_slider[0], period_slider[1]), lang = lang, title = title)
except:
    df = pd.DataFrame()
    
if sammenlign != "":
    tot = sumword(NGRAM, sammenlign, ddk, subject, (period_slider[0], period_slider[1]), lang, title)
else:
    tot = 1

st.line_chart(df.div(tot, axis = 0))

