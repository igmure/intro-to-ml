import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

def desc_calc():
    #obliczenie deskryptora
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

def convert_df(df):
        return df.to_csv().encode('utf-8')

# Model building
def build_model(input_data):
    load_model = pickle.load(open('model.pkl', 'rb'))
    prediction = load_model.predict(input_data)
    st.header('**Przewidziany output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.balloons()
    csv=df.to_csv(index=False)

    st.download_button(
     label="Pobierz plik csv",
     data=csv,
     file_name='prediction.csv',
     mime='text/csv', )


st.markdown("## **Czy twój związek jest bioaktywny w stosunku do prekursowa Alzheimera?**", unsafe_allow_html=False)

image = Image.open('logo.jpg')
st.image(image, use_column_width=False, caption="Twórca: Steppeua / Getty Images")

st.markdown("""
Aplikacja pozwala na przewidzenie, czy dany związek będzie wykazywać zdolności inhibitujące względem prekursora Alzheimera: Beta amyloid A4 protein

**Credits**
- Aplikacja zbudwana w  `Python` + `Streamlit` inspirowana aplikacją [Chanin Nantasenamat](https://medium.com/@chanin.nantasenamat) (aka [Data Professor](http://youtube.com/dataprofessor))
- Deskryptory: [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/) [[Link do artykułu]](https://doi.org/10.1002/jcc.21707).
---
""")

with st.sidebar.header('przekaż plik do analizy'):
    uploaded_file = st.sidebar.file_uploader(label="tutaj udpostępnij swój plik", type=['txt'])
    st.sidebar.markdown("""
[Przykładowy input](https://raw.githubusercontent.com/dataprofessor/bioactivity-prediction-app/main/example_acetylcholinesterase.txt)
""")

if st.sidebar.button('Analiza'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    st.header('**Przekazane dane**')
    st.write(load_data)

    with st.spinner("Obliczanie deskryptorów..."):
        desc_calc()

    # Read in calculated descriptors and display the dataframe
    st.header('**Obliczone deskryptory**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    # Read descriptor list used in previously built model
    st.header('**Podzbiór deskryptorów z poprzednio zbudowanego modelu**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # Apply trained model to make prediction on query compounds
    build_model(desc_subset)
else:
    st.info('Przekaż plik, żeby zacząć!')
