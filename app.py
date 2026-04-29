import streamlit as st
import anthropic
import urllib.parse
import json
import re
import feedparser
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

# =========================
# Configuración de página
# =========================
st.set_page_config(
    page_title="Newsletter SAP",
    page_icon="📰",
    layout="wide"
)

# =========================
# DATOS EMBEBIDOS - Territorios
# =========================
# Estructura: lista de dicts con las columnas del archivo
# Para mantener el código manejable, parseamos el texto directamente

@st.cache_data
def load_territory_data() -> List[Dict]:
    """Carga los datos de territorios embebidos."""
    raw_data = """Diana Garcia Ceballos	Aerospace and Defense	Soledad Novas	COLOMBIA	Nediar S A S
Jorge Pizarro	Aerospace and Defense	Maria José Amezaga	CHILE	Ecocopter
Rodrigo Salgado	Aerospace and Defense	Maria José Amezaga	PERU	Helinka SAC
Micaela Storni	Aerospace and Defense	Soledad Novas	CHILE	Energías Industriales S.A.
Micaela Storni	Aerospace and Defense	Soledad Novas	CHILE	Eurocopter Chile S.A.
Milena Gimenez	Aerospace and Defense	Soledad Novas	ARGENTINA	American Lodging S.A.
Micaela Storni	Aerospace and Defense	Soledad Novas	CHILE	Natvida SPA
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	Campollo S.A.
Milena Gimenez	Agribusiness	Soledad Novas	ARGENTINA	AIBAL SERVICIOS AGROPECUARIOS S.A.
Felipe Rodriguez	Agribusiness	Daniel Castro	COLOMBIA	Diana Corporación S.A.S.
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Galan Litio S.A.
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	Gallego Gonzalez Jose Reinaldo
Diana Romero	Mill Products and Mining	Daniel Castro	COLOMBIA	Alfagres S.A.
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	POLLOS EL BUCANERO S A
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	Nestle De Colombia S.A.
Diana Romero	Professional Services	Daniel Castro	COLOMBIA	Amarey Nova Medical S.A.
Diana Romero	Agribusiness	Daniel Castro	COLOMBIA	Casa Luker S.A.
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	Ci Adm Colombia Ltda
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	Industrias del Maiz S.A.
Diana Romero	Professional Services	Daniel Castro	COLOMBIA	Redeban S.A.
Diana Romero	Wholesale Distribution	Daniel Castro	COLOMBIA	COMERCIALIZADORA INTERNACIONAL BANA
Diana Garcia Ceballos	Agribusiness	Soledad Novas	COLOMBIA	Mobiurbano Agricola S A S
Felipe Rodriguez	Agribusiness	Daniel Castro	COLOMBIA	MAYAGUEZ S.A.
Yadira Castañeda	Agribusiness	Daniel Castro	COLOMBIA	THE ELITE FLOWER S A S C I
Alejandra Guzman	Agribusiness	Daniel Castro	COLOMBIA	Carlos Sarmiento L & Cia Ingenio
Diana Garcia Ceballos	Agribusiness	Soledad Novas	COLOMBIA	AVIAGEN COLOMBIA S A
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	Cargill S.A.C.I.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	COFCO INTERNATIONAL ARGENTINA S.A.
Barbara Rodriguez	Agribusiness	Maria José Amezaga	ARGENTINA	Arcor S.A.I.C.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	ALFRED C. TOEPFER INTERNACIONAL
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	Aceitera General Deheza S.A.
Nahuel Frias	Chemicals	Fernando Oriolo	ARGENTINA	Petroquimica Rio Tercero S.A.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	SWIFT ARGENTINA S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Agrovision Peru S.A.C.
Diana Garcia Ceballos	Agribusiness	Soledad Novas	COLOMBIA	ICOHARINAS SAS
Barbara Rodriguez	Agribusiness	Maria José Amezaga	ARGENTINA	ADECO AGROPECUARIA S.A.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	Amaggi Argentina S/A
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Tensolite S.A.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	Agricultores Federados Argentinos S
Diana Romero	Agribusiness	Daniel Castro	COLOMBIA	AVSA S.A.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	CHS DE ARGENTINA S.A.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	Agrotecnologia y Servicios S.A.
Julian Grinstein	Agribusiness	Maria José Amezaga	ARGENTINA	Vicentin S.A.I.C.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	Ford Argentina S.A.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	Renault Argentina S.A.
Jorge Pizarro	Banking	Maria José Amezaga	CHILE	Banco Santander Chile
Jorge Pizarro	Banking	Maria José Amezaga	CHILE	Banco Estado
Claudia Chirino	Higher Education and Research	Fernando Oriolo	CHILE	Universidad Mayor
Claudia Chirino	Higher Education and Research	Fernando Oriolo	CHILE	Universidad de los Andes
Carolina Latorre	Travel and Transportation	Fernando Oriolo	CHILE	Soc.Conc. Vespucio Norte Express S.
Claudia Chirino	Telecommunications	Fernando Oriolo	CHILE	Claro Chile SpA
Carolina Latorre	Automotive	Fernando Oriolo	CHILE	Nissan Chile, SpA
Carolina Latorre	Mill Products and Mining	Fernando Oriolo	CHILE	Mantos Copper S.A.
Salome Martinez	Retail	Fernando Oriolo	CHILE	Articulos Deportivos Belsport SpA
Salome Martinez	Banking	Fernando Oriolo	CHILE	Caja de Compensación La Araucana
Claudia Chirino	Banking	Fernando Oriolo	CHILE	Transbank S.A.
Carolina Latorre	Life Sciences	Fernando Oriolo	CHILE	Holding Sintex S.A.
Claudia Chirino	Life Sciences	Fernando Oriolo	CHILE	Laboratorios Saval S.A.
Claudia Chirino	Automotive	Fernando Oriolo	CHILE	Kia Chile SpA
Sebastian Figueroa	Public Sector	Maria José Amezaga	CHILE	Camara de Diputados
Jorge Pizarro	Media	Maria José Amezaga	CHILE	Red Televisiva Megavision S.A.
Jorge Pizarro	Life Sciences	Maria José Amezaga	CHILE	Megalabs Chile S.A.
Jorge Pizarro	Utilities	Maria José Amezaga	CHILE	Enorchile S.A.
Salome Martinez	Consumer Products	Fernando Oriolo	CHILE	The Not Company Spa
Salome Martinez	Higher Education and Research	Fernando Oriolo	CHILE	Universidad San Sebastian
Carolina Latorre	Engineering, Construction, and O	Fernando Oriolo	CHILE	EBCO S.A.
Salome Martinez	Mill Products and Mining	Fernando Oriolo	CHILE	Aceros Aza S.A.
Salome Martinez	Travel and Transportation	Fernando Oriolo	CHILE	Jetsmart Airlines SpA
Salome Martinez	Industrial Manufacturing	Fernando Oriolo	CHILE	Celeo Redes Chile Limitada
Carolina Latorre	Insurance	Fernando Oriolo	CHILE	Isapre Banmedica S.A.
Claudia Chirino	Travel and Transportation	Fernando Oriolo	CHILE	Ultramar Agencia Maritima Ltda.
Carolina Latorre	Consumer Products	Fernando Oriolo	CHILE	Dole Chile S.A.
Salome Martinez	Utilities	Fernando Oriolo	CHILE	Guacolda Energia SpA
Salome Martinez	Consumer Products	Fernando Oriolo	CHILE	Copefrut S.A.
Salome Martinez	Insurance	Fernando Oriolo	CHILE	Administradora de Fondos de Pension
Salome Martinez	Retail	Fernando Oriolo	CHILE	Bethia S.A.
Salome Martinez	Retail	Fernando Oriolo	CHILE	Dartel S.A.
Salome Martinez	Consumer Products	Fernando Oriolo	CHILE	Exportadora Unifrutti Traders SpA
Salome Martinez	Consumer Products	Fernando Oriolo	CHILE	Vitafoods SpA
Carolina Latorre	Mill Products and Mining	Fernando Oriolo	CHILE	Prodalam S.A.
Carolina Latorre	Mill Products and Mining	Fernando Oriolo	CHILE	Mantos Copper S.A.
Carolina Latorre	Mill Products and Mining	Fernando Oriolo	CHILE	Fabrica de Pernos y Tornillos Ameri
Carolina Latorre	Mill Products and Mining	Fernando Oriolo	CHILE	Minera Valle Central S.A.
Carolina Latorre	Travel and Transportation	Fernando Oriolo	CHILE	CPT Empresas Maritimas S A
Carolina Latorre	Professional Services	Fernando Oriolo	CHILE	Vivo SpA
Carolina Latorre	Engineering, Construction, and O	Fernando Oriolo	CHILE	Constructora Socovesa Santiago S.A.
Carolina Latorre	Engineering, Construction, and O	Fernando Oriolo	CHILE	Cia. Industrial El Volcan S.A.
Carolina Latorre	Public Sector	Fernando Oriolo	CHILE	Fundacion Integra
Carolina Latorre	Agribusiness	Fernando Oriolo	CHILE	Blumar S.A.
Carolina Latorre	Agribusiness	Fernando Oriolo	CHILE	Salmones Aysen S.A.
Carolina Latorre	Wholesale Distribution	Fernando Oriolo	CHILE	ASF Logistica SpA
Claudia Chirino	Mill Products and Mining	Fernando Oriolo	CHILE	KGHM Chile Spa.
Claudia Chirino	Public Sector	Fernando Oriolo	CHILE	Corporacion de Fomento de la Produc
Claudia Chirino	Professional Services	Fernando Oriolo	CHILE	Martinez y Valdivieso S.A.
Claudia Chirino	Higher Education and Research	Fernando Oriolo	CHILE	Universidad Diego Portales
Claudia Chirino	Higher Education and Research	Fernando Oriolo	CHILE	Fundacion Educacion y Cultura
Claudia Chirino	Higher Education and Research	Fernando Oriolo	CHILE	Universidad Central de Chile
Claudia Chirino	Telecommunications	Fernando Oriolo	CHILE	Infraco SpA
Claudia Chirino	Travel and Transportation	Fernando Oriolo	CHILE	Mathiesen S.A.C.
Claudia Chirino	Agribusiness	Fernando Oriolo	CHILE	Duncan Fox
Nahuel Frias	Chemicals	Fernando Oriolo	ARGENTINA	Petroquimica Rio Tercero S.A.
Nahuel Frias	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Industrias Juan F. Secco
Nahuel Frias	Mill Products and Mining	Fernando Oriolo	ARGENTINA	VICUÑA ARGENTINA S. A.
Nahuel Frias	Wholesale Distribution	Fernando Oriolo	ARGENTINA	Supermercados Mayoristas Yaguar S.A
Nahuel Frias	Professional Services	Fernando Oriolo	ARGENTINA	IMS Argentina S.R.L
Nahuel Frias	Consumer Products	Fernando Oriolo	ARGENTINA	S.A. San Miguel A.G.I.C.I. y F.
Nahuel Frias	Agribusiness	Fernando Oriolo	ARGENTINA	GDM Argentina S.A.
Nahuel Frias	Travel and Transportation	Fernando Oriolo	ARGENTINA	Organizacion Courier Argentina S.A.
Nahuel Frias	Oil, Gas, and Energy	Fernando Oriolo	ARGENTINA	Oleoductos del Valle S.A.
Nahuel Frias	Retail	Fernando Oriolo	ARGENTINA	Naldo Lombardi S.A.
Nahuel Frias	Retail	Fernando Oriolo	ARGENTINA	Blue Star Group S.A
Nahuel Frias	Wholesale Distribution	Fernando Oriolo	ARGENTINA	Farmanet S.A.
Nahuel Frias	Banking	Fernando Oriolo	ARGENTINA	Grupo Piero S.A.
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Galan Litio S.A.
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Tensolite S.A.
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Bertotto Boglione S.A.
Veronica Ares	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Grupo Ayudin Argentina S.A.
Veronica Ares	Consumer Products	Fernando Oriolo	ARGENTINA	Cafes La Virginia S.A.
Veronica Ares	Life Sciences	Fernando Oriolo	ARGENTINA	Wiener Laboratorios S.A.I.C.
Veronica Ares	Industrial Manufacturing	Fernando Oriolo	ARGENTINA	PC Arts Argentina S.A.
Veronica Ares	Agribusiness	Fernando Oriolo	ARGENTINA	Union Agricola De Avellaneda Coop.
Veronica Ares	Agribusiness	Fernando Oriolo	ARGENTINA	Frimsa S.A.
Veronica Ares	Agribusiness	Fernando Oriolo	ARGENTINA	Bunge Argentina S.A.
Veronica Ares	Oil, Gas, and Energy	Fernando Oriolo	ARGENTINA	Distribuidora De Gas Cuyana S.A.
Veronica Ares	Automotive	Fernando Oriolo	ARGENTINA	Talleres Metalurgicos Crucianelli,
Federico Martinez	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Minera Exar S.A.
Federico Martinez	Mill Products and Mining	Fernando Oriolo	ARGENTINA	Industria del Plastico y Metalurgic
Federico Martinez	Consumer Products	Fernando Oriolo	ARGENTINA	Cepas Argentinas S.A.
Federico Martinez	Consumer Products	Fernando Oriolo	ARGENTINA	Fratelli Branca Destilerías S.A.
Federico Martinez	Consumer Products	Fernando Oriolo	ARGENTINA	DREAMCO S.A.
Federico Martinez	Consumer Products	Fernando Oriolo	ARGENTINA	Reginald Lee S.A.
Federico Martinez	Professional Services	Fernando Oriolo	ARGENTINA	Qactions System S.R.L.
Federico Martinez	Professional Services	Fernando Oriolo	ARGENTINA	BAITCON S.A.
Federico Martinez	Retail	Fernando Oriolo	ARGENTINA	London Free Zone S.A.
Alejandro Nunez	Wholesale Distribution	Fernando Oriolo	ARGENTINA	Aguas S.R.L.
Alejandro Nunez	Media	Fernando Oriolo	ARGENTINA	Dridco S.A.U.
Alejandro Nunez	Media	Fernando Oriolo	ARGENTINA	SA La Nacion
Alejandro Nunez	Life Sciences	Fernando Oriolo	ARGENTINA	Genomma Laboratories Argentina S.A.
Alejandro Nunez	Life Sciences	Fernando Oriolo	ARGENTINA	Baliarda S.A.
Alejandro Nunez	Retail	Fernando Oriolo	ARGENTINA	Ricardo Nini S.A.
Alejandro Nunez	Engineering, Construction, and O	Fernando Oriolo	ARGENTINA	Genneia S.A.
Alejandro Nunez	Consumer Products	Fernando Oriolo	ARGENTINA	Vestiditos S.A.
Alejandro Nunez	Consumer Products	Fernando Oriolo	ARGENTINA	LDC ARGENTINA SA
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Agrovision Peru S.A.C.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Redondos S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Viru Group Peru S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Complejo Agroindustrial Beta S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Pesquera Exalmar S.A.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Arato Peru S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Danper Trujillo S.A.C.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	La Calera S.A.C.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	El Pedregal, S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Conservera De Las Americas S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	El Rocio S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Agroindustrias AIB S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Gandules Inc. S.A.C.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	San Miguel Fruits Peru S.A.
Gonzalo Delosrios	Agribusiness	Fernando Oriolo	PERU	Grupo Santa Elena S.A.
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU	Laive S.A.
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU	Agroindustrial Laredo S.A.A.
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU	Agricola Cerro Prieto S.A.
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU	Agro Industrial Paramonga S.A.
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU	Blue Pacific Oils S.A.C.
Carlos Yepez	Agribusiness	Fernando Oriolo	PERU	Supergen S.A.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Ipesa S.A.C.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Promotora Genesis S.A.C.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Grupo Pana S.A.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Crosland Motos S.A.C.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Toyota del Peru S.A.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Maquinarias S.A
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Gestion de Servicios Ambientales S.
Carlos Yepez	Automotive	Fernando Oriolo	PERU	Freno S.A.
Salome Martinez	Agribusiness	Fernando Oriolo	CHILE	Frigorifico Temuco S.A.
Salome Martinez	Wholesale Distribution	Fernando Oriolo	CHILE	Reutter S.A.
Salome Martinez	Banking	Fernando Oriolo	CHILE	Inversiones Arion SPA
Juan Duran	Agribusiness	Daniel Castro	COLOMBIA	Manuelita Corporativa S.A.S.
Juan Duran	Oil, Gas, and Energy	Daniel Castro	COLOMBIA	Mansarovar Energy Colombia Ltda.
Juan Duran	Oil, Gas, and Energy	Daniel Castro	COLOMBIA	Biomax Biocombustibles S.A.
Juan Duran	Life Sciences	Daniel Castro	COLOMBIA	JGB S.A.
Angie Monroy	Automotive	Daniel Castro	COLOMBIA	Automotores Toyota Colombia S A S
Felipe Rodriguez	Automotive	Daniel Castro	COLOMBIA	COMPAÑIA COLOMBIANA DE SERVICIO
Angie Monroy	Automotive	Daniel Castro	COLOMBIA	ZONA FRANCA INDUSTRIAL COLMOTORES S
Felipe Rodriguez	Automotive	Daniel Castro	COLOMBIA	Renault Sociedad De Fabricacion
Felipe Rodriguez	Automotive	Daniel Castro	COLOMBIA	General Motors Colmotores S.A.
Felipe Rodriguez	Automotive	Daniel Castro	COLOMBIA	Mazda de Colombia S.A.S.
Angie Monroy	Banking	Daniel Castro	COLOMBIA	Scotiabank Colpatria S.A.
Angie Monroy	Banking	Daniel Castro	COLOMBIA	CITIBANK COLOMBIA S A
Alejandro Roncancio	Banking	Daniel Castro	COLOMBIA	ITAU CORPBANCA COLOMBIA S.A.
Alejandro Roncancio	Banking	Daniel Castro	COLOMBIA	Credibanco S A
Alejandro Roncancio	Banking	Daniel Castro	COLOMBIA	Cifin S.A.
Alejandro Roncancio	Banking	Daniel Castro	COLOMBIA	Bolsa de Valores de Colombia S.A.
Alejandro Roncancio	Agribusiness	Daniel Castro	COLOMBIA	Industrias Puropollo S.A.
Diana Romero	Consumer Products	Daniel Castro	COLOMBIA	SUPER DE ALIMENTOS S.A.S.
Diana Romero	Consumer Products	Daniel Castro	COLOMBIA	Cueros Velez S.A.S.
Diana Romero	Retail	Daniel Castro	COLOMBIA	Comercializadora Arturo Calle S.A.S
Diana Romero	Mill Products and Mining	Daniel Castro	COLOMBIA	Cerro Matoso, S.A.
Diana Romero	Mill Products and Mining	Daniel Castro	COLOMBIA	Carbomax de Colombia S A S
Diana Romero	Mill Products and Mining	Daniel Castro	COLOMBIA	Cartones América S.A.
Diana Romero	Mill Products and Mining	Daniel Castro	COLOMBIA	Alfagres S.A.
Gurin Arauco	Automotive	Maria José Amezaga	PERU	Derco Perú S.A.
Gurin Arauco	Automotive	Maria José Amezaga	PERU	International Camiones Del Perú S.A
Gurin Arauco	Automotive	Maria José Amezaga	PERU	Inchcape Latam Perú S.A.
Gurin Arauco	Automotive	Maria José Amezaga	PERU	General Motors Perú S.A.
Gurin Arauco	Automotive	Maria José Amezaga	PERU	Volvo Peru S A
Gurin Arauco	Mill Products and Mining	Maria José Amezaga	PERU	Michell y Cia. S.A.
Gurin Arauco	Mill Products and Mining	Maria José Amezaga	PERU	Owens Illinois Peru S.A.
Gurin Arauco	Chemicals	Maria José Amezaga	PERU	Industrias Electro Químicas S.A.
Gurin Arauco	Chemicals	Maria José Amezaga	PERU	BASF Peruana S.A.
Gurin Arauco	Chemicals	Maria José Amezaga	PERU	Lapices y Conexos S.A.
Gurin Arauco	Chemicals	Maria José Amezaga	PERU	Dispercol S.A.
Gurin Arauco	Oil, Gas, and Energy	Maria José Amezaga	PERU	Maple Gas Corporation del Perú S.R.
Gurin Arauco	Oil, Gas, and Energy	Maria José Amezaga	PERU	Negociacion Kio S.A.C.
Gurin Arauco	Oil, Gas, and Energy	Maria José Amezaga	PERU	Llama Gas S.A.
Gurin Arauco	Public Sector	Maria José Amezaga	PERU	Superintendencia de Banca, Seguros
Gurin Arauco	Public Sector	Maria José Amezaga	PERU	Agencia De Promocion De La Inversio
Gurin Arauco	Utilities	Maria José Amezaga	PERU	Genrent Del Perú S.A.C.
Gurin Arauco	Banking	Maria José Amezaga	PERU	NIAGARA ENERGY S.A.C.
Maria Teresa Romero	Insurance	Maria José Amezaga	PERU	Ohio National Seguros de Vida S.A.
Maria Teresa Romero	Banking	Maria José Amezaga	PERU	Alfin Banco S.A.
Maria Teresa Romero	Banking	Maria José Amezaga	PERU	Banco de la Nacion
Maria Teresa Romero	Banking	Maria José Amezaga	PERU	Banco Pichincha
Maria Teresa Romero	Banking	Maria José Amezaga	PERU	CMAC Arequipa S.A.
Maria Teresa Romero	Healthcare	Maria José Amezaga	PERU	Hospital Nacional Dos de Mayo
Maria Teresa Romero	Healthcare	Maria José Amezaga	PERU	Adm. Clinica Ricardo Palma S.A.
Maria Teresa Romero	Consumer Products	Maria José Amezaga	PERU	Textil Del Valle S.A. BIC
Maria Teresa Romero	Consumer Products	Maria José Amezaga	PERU	Precotex S.A.C.
Maria Teresa Romero	Professional Services	Maria José Amezaga	PERU	Hermes Transportes Blindados S.A.
Maria Teresa Romero	Professional Services	Maria José Amezaga	PERU	G4S PERU S.A.C.
Maria Teresa Romero	Media	Maria José Amezaga	PERU	Publicis Asociados S.A.C.
Rodrigo Salgado	Wholesale Distribution	Maria José Amezaga	PERU	DELL
Rodrigo Salgado	Wholesale Distribution	Maria José Amezaga	PERU	Johnson & Johnson del Peru S.A.
Rodrigo Salgado	Wholesale Distribution	Maria José Amezaga	PERU	Mayorsa S.A.
Rodrigo Salgado	Engineering, Construction, and O	Maria José Amezaga	PERU	Autopista del Norte S.A.C.
Rodrigo Salgado	Engineering, Construction, and O	Maria José Amezaga	PERU	V & V Bravo S.A.C.
Rodrigo Salgado	Engineering, Construction, and O	Maria José Amezaga	PERU	Odebrecht Latinvest Peru S.A.C.
Rodrigo Salgado	Engineering, Construction, and O	Maria José Amezaga	PERU	Administradora Jockey Plaza Shoppin
Rodrigo Salgado	Higher Education and Research	Maria José Amezaga	PERU	Colegios Peruanos S.A.C. - Sucursal
Rodrigo Salgado	Higher Education and Research	Maria José Amezaga	PERU	Universidad Privada Antenor Orrego
Rodrigo Salgado	Retail	Maria José Amezaga	PERU	JORSA DE LA SELVA S.A.
Rodrigo Salgado	Retail	Maria José Amezaga	PERU	Manufacturas San Isidro S.A.C.
Rodrigo Salgado	Travel and Transportation	Maria José Amezaga	PERU	Servosa Cargo S.A.C.
Rodrigo Salgado	Travel and Transportation	Maria José Amezaga	PERU	DHL Global Forwarding Aduanas Peru
Barbara Rodriguez	Chemicals	Maria José Amezaga	ARGENTINA	QUIMICA CALLEGARI S.R.L.
Barbara Rodriguez	Chemicals	Maria José Amezaga	ARGENTINA	MAPEI ARGENTINA S.A.
Barbara Rodriguez	Chemicals	Maria José Amezaga	ARGENTINA	INDUSTRIAS SICA S.A.I.C.
Barbara Rodriguez	Chemicals	Maria José Amezaga	ARGENTINA	Grupo Inplast, S.A.
Barbara Rodriguez	Chemicals	Maria José Amezaga	ARGENTINA	Evonik Metilatos
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Yacimiento Carbonífero Río Turbio
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Gnc Galileo Sa
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	JC Decaux OOH Argentina S.A.
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Limansky, S.A.
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Klabin Argentina S.A.
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Industrias Cormetal S.A.
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Majdalani inox SA
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Transportes Rada Tilly S.A.
Barbara Rodriguez	Mill Products and Mining	Maria José Amezaga	ARGENTINA	Lartex S.R.L.
Barbara Rodriguez	Wholesale Distribution	Maria José Amezaga	ARGENTINA	TERRAMAR JV S.A.
Barbara Rodriguez	Wholesale Distribution	Maria José Amezaga	ARGENTINA	Philips Argentina S.A.
Barbara Rodriguez	Wholesale Distribution	Maria José Amezaga	ARGENTINA	COVEMA S.A.C.I.F.
Barbara Rodriguez	Wholesale Distribution	Maria José Amezaga	ARGENTINA	MEDTRONIC LATIN AMERICA INC.
Barbara Rodriguez	Retail	Maria José Amezaga	ARGENTINA	La Dolce S.R.L.
Barbara Rodriguez	Retail	Maria José Amezaga	ARGENTINA	NEWTON STATION SRL
Barbara Rodriguez	Professional Services	Maria José Amezaga	ARGENTINA	Simmons De Argentina S.A.I.C.
Barbara Rodriguez	Agribusiness	Maria José Amezaga	ARGENTINA	Arcor S.A.I.C.
Barbara Rodriguez	Agribusiness	Maria José Amezaga	ARGENTINA	ADECO AGROPECUARIA S.A.
Joaquin Biagini	Healthcare	Maria José Amezaga	ARGENTINA	Tecnoimagen S.A.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	FRANKLIN SANTIAGO BOGLICH S.R.L.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	MAXION MONTICH S.A.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	Ford Argentina S.A.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	Renault Argentina S.A.
Joaquin Biagini	Automotive	Maria José Amezaga	ARGENTINA	GENERAL MOTORS DE ARGENTINA S.R.L.
Joaquin Biagini	Banking	Maria José Amezaga	ARGENTINA	Banco Credicoop Coop. Ltdo.
Joaquin Biagini	Banking	Maria José Amezaga	ARGENTINA	Banco BBVA Argentina S.A.
Joaquin Biagini	Banking	Maria José Amezaga	ARGENTINA	Industrial and Commercial Bank of C
Joaquin Biagini	Banking	Maria José Amezaga	ARGENTINA	Banco Patagonia S.A.
Joaquin Biagini	Professional Services	Maria José Amezaga	ARGENTINA	Luis Losi S.A.
Joaquin Biagini	Media	Maria José Amezaga	ARGENTINA	EYEWORKS ARGENTINA S.A.
Julian Grinstein	Oil, Gas, and Energy	Maria José Amezaga	ARGENTINA	PAMPETROL S.A.P.E.M.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	INTERNATIONAL FLAVORS & FRAGRANCES
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	Gastaldi Hermanos, S.A.I.C.F.E.I.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	Productora Del Noroeste S.A.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	Ecolab Argentina S.R.L.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	Briket SA
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	David Rosental E Hijos S.A.C.I.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	Advance Organic Materials S.A
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	SAF Argentina S.A.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	JBS Leather Argentina S.A.
Julian Grinstein	Consumer Products	Maria José Amezaga	ARGENTINA	Frigorifico Riosma Sociedad Anonima
Julian Grinstein	Engineering, Construction, and O	Maria José Amezaga	ARGENTINA	BOETTO Y BUTTIGLIENGO S.A.
Julian Grinstein	Engineering, Construction, and O	Maria José Amezaga	ARGENTINA	Grupo Concesionario del Oeste S.A.
Julian Grinstein	Engineering, Construction, and O	Maria José Amezaga	ARGENTINA	Jcr S. A.
Julian Grinstein	Industrial Manufacturing	Maria José Amezaga	ARGENTINA	Wenlen S.A.
Sebastian Figueroa	Agribusiness	Maria José Amezaga	CHILE	AGRICOLA AGROBERRIES LIMITADA
Sebastian Figueroa	Agribusiness	Maria José Amezaga	CHILE	Pesquera La Portada S.A.
Sebastian Figueroa	Agribusiness	Maria José Amezaga	CHILE	Agroindustrial El Paico S.A.
Sebastian Figueroa	Wholesale Distribution	Maria José Amezaga	CHILE	Puratos de Chile, S.A.
Sebastian Figueroa	Wholesale Distribution	Maria José Amezaga	CHILE	Sandvik Credit Chile S.A.
Sebastian Figueroa	Chemicals	Maria José Amezaga	CHILE	Quimetal Industrial S.A.
Sebastian Figueroa	Mill Products and Mining	Maria José Amezaga	CHILE	Prefabricados de Hormigon Grau S.A.
Sebastian Figueroa	Mill Products and Mining	Maria José Amezaga	CHILE	Astillas Exportaciones, Ltda.
Sebastian Figueroa	Consumer Products	Maria José Amezaga	CHILE	Importadora y Distribuidora Arquime
Sebastian Figueroa	Industrial Manufacturing	Maria José Amezaga	CHILE	CEM S.A.
Sebastian Figueroa	Travel and Transportation	Maria José Amezaga	CHILE	Compania Naviera Frasal S.A
Sebastian Figueroa	Travel and Transportation	Maria José Amezaga	CHILE	Tnt Express Chile Limitada
Sebastian Figueroa	Retail	Maria José Amezaga	CHILE	Audiomusica S.A.
Sebastian Figueroa	Higher Education and Research	Maria José Amezaga	CHILE	Centro De Estudios Paramedicos Y
Sebastian Figueroa	Higher Education and Research	Maria José Amezaga	CHILE	Universidad De Los Lagos
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	DFMC SpA
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	Automotores Gildemeister SpA
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	Comercial Chrysler
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	Comercial Automotriz S.A.
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	Scania Chile S.A.
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	PSA Chile S.A.
Jorge Pizarro	Automotive	Maria José Amezaga	CHILE	Bruno Fritsch S.A.
Jorge Pizarro	Banking	Maria José Amezaga	CHILE	Inversiones Salta S.A.
Jorge Pizarro	Banking	Maria José Amezaga	CHILE	Inversiones Consolidadas S. A.
Jorge Pizarro	Banking	Maria José Amezaga	CHILE	Scotiabank Chile
Jorge Pizarro	Banking	Maria José Amezaga	CHILE	Banco Consorcio
Jorge Pizarro	Insurance	Maria José Amezaga	CHILE	Caja Reaseguradora De Chile S.A.
Jorge Pizarro	Professional Services	Maria José Amezaga	CHILE	Marketing y Promociones SA
Jorge Pizarro	Professional Services	Maria José Amezaga	CHILE	Automática y Regulación S.A.
Jorge Pizarro	Professional Services	Maria José Amezaga	CHILE	Stefanini Chile S. A.
Jorge Pizarro	Professional Services	Maria José Amezaga	CHILE	Empresa Constructora SIGRO SA
Jorge Pizarro	Engineering, Construction, and O	Maria José Amezaga	CHILE	Constructora Avellaneda, Ltda.
Jorge Pizarro	Engineering, Construction, and O	Maria José Amezaga	CHILE	Desco S.A. Constructora
Jorge Pizarro	Life Sciences	Maria José Amezaga	CHILE	Fresenuis Medical Care Chile
Jorge Pizarro	Media	Maria José Amezaga	CHILE	Canal 13 S.A."""

    records = []
    for line in raw_data.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) >= 5:
            records.append({
                "ae": parts[0].strip(),
                "industry": parts[1].strip(),
                "manager": parts[2].strip(),
                "country": parts[3].strip().upper(),
                "planning_entity": parts[4].strip()
            })
    return records


def get_country_data(data: List[Dict], country: str) -> Dict:
    """Extrae información organizada por país."""
    country_upper = country.upper()
    filtered = [r for r in data if r["country"] == country_upper]

    # AEs únicos
    aes = list(set(r["ae"] for r in filtered))

    # Industrias únicas
    industries = list(set(r["industry"] for r in filtered))

    # Planning entities por industria
    entities_by_industry = defaultdict(set)
    for r in filtered:
        entities_by_industry[r["industry"]].add(r["planning_entity"])

    # Planning entities completas (para excluir)
    all_entities = set(r["planning_entity"] for r in filtered)

    # AEs por industria
    aes_by_industry = defaultdict(set)
    for r in filtered:
        aes_by_industry[r["industry"]].add(r["ae"])

    # Managers únicos
    managers = list(set(r["manager"] for r in filtered))

    return {
        "aes": sorted(aes),
        "industries": sorted(industries),
        "entities_by_industry": {k: sorted(v) for k, v in entities_by_industry.items()},
        "all_entities": all_entities,
        "aes_by_industry": {k: sorted(v) for k, v in aes_by_industry.items()},
        "managers": sorted(managers),
        "records": filtered
    }


# =========================
# Configuración de emails por AE
# =========================
AE_EMAILS = {
    "Agustina Landi": "agustina.landi@sap.com",
    "Diana Garcia Ceballos": "diana.garcia.ceballos@sap.com",
    "Jorge Pizarro": "jorge.pizarro@sap.com",
    "Rodrigo Salgado": "rodrigo.salgado@sap.com",
    "Micaela Storni": "micaela.storni@sap.com",
    "Milena Gimenez": "milena.gimenez@sap.com",
    "Alejandra Guzman": "alejandra.guzman@sap.com",
    "Felipe Rodriguez": "felipe.rodriguez@sap.com",
    "Veronica Ares": "veronica.ares@sap.com",
    "Diana Romero": "diana.romero@sap.com",
    "Julian Grinstein": "julian.grinstein@sap.com",
    "Nahuel Frias": "nahuel.frias@sap.com",
    "Barbara Rodriguez": "barbara.rodriguez@sap.com",
    "Joaquin Biagini": "joaquin.biagini@sap.com",
    "Gonzalo Delosrios": "gonzalo.delosrios@sap.com",
    "Carlos Yepez": "carlos.yepez@sap.com",
    "Maria Teresa Romero": "maria.teresa.romero@sap.com",
    "Gurin Arauco": "gurin.arauco@sap.com",
    "Sebastian Figueroa": "sebastian.figueroa@sap.com",
    "Carolina Latorre": "carolina.latorre@sap.com",
    "Claudia Chirino": "claudia.chirino@sap.com",
    "Salome Martinez": "salome.martinez@sap.com",
    "Noelia Madeo": "noelia.madeo@sap.com",
    "Pilar Nunez Pessano": "pilar.nunez.pessano@sap.com",
    "Lucila Moglianesi": "lucila.moglianesi@sap.com",
    "Sofia Pepe": "sofia.pepe@sap.com",
    "Angie Monroy": "angie.monroy@sap.com",
    "Alejandro Roncancio": "alejandro.roncancio@sap.com",
    "Juan Duran": "juan.duran@sap.com",
    "Yadira Castañeda": "yadira.castaneda@sap.com",
    "Federico Martinez": "federico.martinez@sap.com",
    "Alejandro Nunez": "alejandro.nunez@sap.com",
}

CC_EMAILS = ["julieta.rigi@sap.com", "nicolas.araneda@sap.com", "luis.plazas@sap.com"]

COUNTRIES = ["ARGENTINA", "CHILE", "PERU", "COLOMBIA"]
COUNTRY_DISPLAY = {
    "ARGENTINA": "Argentina",
    "CHILE": "Chile",
    "PERU": "Perú",
    "COLOMBIA": "Colombia"
}
COUNTRY_FLAGS = {
    "ARGENTINA": "🇦🇷",
    "CHILE": "🇨🇱",
    "PERU": "🇵🇪",
    "COLOMBIA": "🇨🇴"
}

# =========================
# Estilos CSS
# =========================
st.markdown("""
<style>
    .sap-hero {
        background: linear-gradient(120deg, #003A8C 0%, #0057D9 65%, #0070F2 100%);
        border-radius: 18px;
        padding: 28px 32px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,.18);
    }
    .sap-badge {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 10px;
        background: rgba(255,255,255,.18);
        margin-right: 8px;
        font-size: 12px;
        font-weight: 600;
    }
    .step-header {
        background: linear-gradient(90deg, #003A8C, #0057D9);
        color: white;
        padding: 10px 18px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 16px;
        margin: 20px 0 12px 0;
    }
    .news-card {
        border: 1px solid #DBEAFE;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background: #F8FBFF;
    }
    .industry-header {
        background: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 8px 14px;
        border-radius: 0 8px 8px 0;
        margin: 16px 0 10px 0;
        font-weight: 700;
        color: #1E3A5F;
    }
    .entity-tag {
        display: inline-block;
        background: #DBEAFE;
        color: #1E40AF;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        margin: 2px;
    }
    .sap-alert {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        color: #9A3412;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 16px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Hero
# =========================
st.markdown("""
<div class="sap-hero">
    <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
        <div style="background:#fff; color:#0057D9; border-radius:8px;
                    font-weight:700; padding:8px 12px; font-size:18px;">SAP</div>
        <div style="font-weight:600; opacity:.9; font-size:15px;">
            Operations Team · Newsletter Intelligence
        </div>
    </div>
    <h1 style="margin:0; font-size:38px; line-height:1.05;">Newsletter por País</h1>
    <p style="margin:10px 0 16px 0; font-size:16px; opacity:.92;">
        Noticias reales · Segmentadas por industria · Cuentas nuevas · Envío por Outlook
    </p>
    <span class="sap-badge">🇦🇷 Argentina</span>
    <span class="sap-badge">🇨🇱 Chile</span>
    <span class="sap-badge">🇵🇪 Perú</span>
    <span class="sap-badge">🇨🇴 Colombia</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sap-alert">
    <b>⚠ Aviso:</b> Las noticias se obtienen de Google News RSS (fuentes reales).
    El análisis ejecutivo es generado por IA. Valida siempre antes del envío.
</div>
""", unsafe_allow_html=True)

# =========================
# Claude API
# =========================
def get_api_key() -> Optional[str]:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        pass
    import os
    return os.getenv("ANTHROPIC_API_KEY")


def call_claude(prompt: str, max_tokens: int = 2048) -> str:
    api_key = get_api_key()
    if not api_key:
        st.error("❌ API Key no configurada. Agrega ANTHROPIC_API_KEY en Secrets.")
        st.stop()
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


# =========================
# Google News RSS - Noticias reales
# =========================
def search_google_news(query: str, country_code: str = "", max_results: int = 10) -> List[Dict]:
    """Busca noticias reales en Google News RSS."""
    # Mapeo de país a código de Google News
    country_gl = {
        "ARGENTINA": "AR",
        "CHILE": "CL",
        "PERU": "PE",
        "COLOMBIA": "CO"
    }
    country_hl = {
        "ARGENTINA": "es-419",
        "CHILE": "es-419",
        "PERU": "es-419",
        "COLOMBIA": "es-419"
    }

    gl = country_gl.get(country_code, "")
    hl = country_hl.get(country_code, "es-419")

    encoded_query = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl={hl}&gl={gl}&ceid={gl}:es-419"

    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:max_results]:
            # Extraer fuente del título (Google News format: "Título - Fuente")
            title = entry.get("title", "")
            source = ""
            if " - " in title:
                parts = title.rsplit(" - ", 1)
                title = parts[0]
                source = parts[1] if len(parts) > 1 else ""

            pub_date = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    from time import mktime
                    dt = datetime.fromtimestamp(mktime(entry.published_parsed))
                    pub_date = dt.strftime("%d/%m/%Y")
                except Exception:
                    pub_date = entry.get("published", "")[:10]

            results.append({
                "title": title,
                "source": source,
                "url": entry.get("link", ""),
                "date": pub_date,
                "summary": entry.get("summary", "")[:200]
            })
        return results
    except Exception as e:
        st.warning(f"Error buscando noticias para '{query}': {str(e)}")
        return []


def search_industry_news(industry: str, country: str,
                         existing_entities: Set[str],
                         max_results: int = 10) -> List[Dict]:
    """Busca noticias de una industria en un país, excluyendo cuentas existentes."""

    # Mapeo de industrias a términos de búsqueda en español
    industry_search_terms = {
        "Aerospace and Defense": "industria aeroespacial defensa",
        "Agribusiness": "agroindustria agro agricultura",
        "Automotive": "industria automotriz autos vehículos",
        "Banking": "banca finanzas bancos fintech",
        "Chemicals": "industria química químicos",
        "Consumer Products": "productos consumo masivo alimentos bebidas",
        "Engineering, Construction, and O": "construcción ingeniería infraestructura",
        "Healthcare": "salud hospitales clínicas",
        "Higher Education and Research": "educación universidades",
        "Industrial Manufacturing": "manufactura industrial fábricas",
        "Insurance": "seguros aseguradoras",
        "Life Sciences": "farmacéutica laboratorios ciencias vida",
        "Media": "medios comunicación televisión digital",
        "Mill Products and Mining": "minería metalurgia acero",
        "Oil, Gas, and Energy": "petróleo gas energía renovable",
        "Professional Services": "servicios profesionales consultoría",
        "Public Sector": "sector público gobierno",
        "Retail": "retail comercio tiendas ecommerce",
        "Telecommunications": "telecomunicaciones telecom 5G",
        "Travel and Transportation": "transporte logística turismo aviación",
        "Utilities": "servicios públicos electricidad agua",
        "Wholesale Distribution": "distribución mayorista logística"
    }

    country_names = {
        "ARGENTINA": "Argentina",
        "CHILE": "Chile",
        "PERU": "Perú",
        "COLOMBIA": "Colombia"
    }

    search_term = industry_search_terms.get(industry, industry)
    country_name = country_names.get(country, country)

    # Buscar noticias nuevas empresas + industria + país
    query = f"{search_term} empresas nuevas {country_name} 2025"
    raw_news = search_google_news(query, country, max_results=max_results + 5)

    # Filtrar noticias que mencionen cuentas existentes
    filtered = []
    for news in raw_news:
        title_lower = news["title"].lower()
        is_existing = False
        for entity in existing_entities:
            # Verificar si alguna palabra clave de la entidad aparece en el título
            entity_words = entity.lower().split()
            # Usar las primeras 2 palabras significativas
            key_words = [w for w in entity_words if len(w) > 3][:2]
            if key_words and all(w in title_lower for w in key_words):
                is_existing = True
                break
        if not is_existing:
            news["industry"] = industry
            filtered.append(news)

        if len(filtered) >= max_results:
            break

    return filtered[:max_results]


# =========================
# Profundizar noticia con Claude
# =========================
def deepen_news_item(title: str, source: str, industry: str, country: str) -> str:
    prompt = (
        f"Eres un analista de negocios senior especializado en tecnología empresarial y SAP.\n\n"
        f"Noticia real: \"{title}\"\n"
        f"Fuente: {source}\n"
        f"País: {country}\n"
        f"Industria: {industry}\n\n"
        f"Escribe un resumen ejecutivo con exactamente estas 3 secciones:\n"
        f"CONTEXTO: (2-3 oraciones sobre qué está pasando y por qué importa)\n"
        f"IMPACTO B2B: (2-3 oraciones sobre cómo afecta a empresas medianas y grandes)\n"
        f"OPORTUNIDAD SAP: (1-2 oraciones sobre qué solución SAP es relevante)\n\n"
        f"Tono profesional y directo. Máximo 120 palabras en total.\n"
        f"Responde solo el texto con las etiquetas CONTEXTO:, IMPACTO B2B:, OPORTUNIDAD SAP:"
    )
    return call_claude(prompt, max_tokens=400)


# =========================
# Construir HTML del newsletter
# =========================
def build_news_item_html(item: Dict, deep_text: str) -> str:
    deep_block = ""
    if deep_text:
        lines = [l.strip() for l in deep_text.split("\n") if l.strip()]
        paragraphs = "".join(
            f"<p style='margin:4px 0; font-size:13px; color:#1F2937;'>{l}</p>"
            for l in lines
        )
        deep_block = (
            "<div style='background:#F0FDF4; border-left:4px solid #22C55E;"
            "border-radius:6px; padding:12px 14px; margin-top:10px;'>"
            "<p style='margin:0 0 6px 0; font-weight:700; color:#15803D;"
            "font-size:11px; text-transform:uppercase;'>📊 Análisis Ejecutivo</p>"
            + paragraphs +
            "</div>"
        )

    return (
        f"<div style='border:1px solid #DBEAFE; border-radius:10px;"
        f"padding:14px 16px; margin-bottom:12px; background:#F8FBFF;'>"
        f"<a href='{item['url']}' style='color:#1D4ED8; text-decoration:none;"
        f"font-weight:700; font-size:15px; line-height:1.4;'>{item['title']}</a>"
        f"<p style='margin:5px 0 0 0; color:#6B7280; font-size:12px;'>"
        f"📰 {item['source']} &nbsp;|&nbsp; 🏭 {item.get('industry', '')} "
        f"&nbsp;|&nbsp; 📅 {item.get('date', '')}</p>"
        + deep_block +
        "</div>"
    )


def build_full_newsletter_html(
    country: str,
    news_by_industry: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str,
    aes: List[str]
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    flag = COUNTRY_FLAGS.get(country, "🌎")
    display_name = COUNTRY_DISPLAY.get(country, country)

    total_news = sum(len(v) for v in news_by_industry.values())

    # Secciones por industria
    sections_html = ""
    for industry in sorted(news_by_industry.keys()):
        items = news_by_industry[industry]
        if not items:
            continue

        items_html = ""
        for item in items:
            key = f"{country}_{industry}_{item['title'][:50]}"
            deep_text = deep_content.get(key, "")
            items_html += build_news_item_html(item, deep_text)

        sections_html += (
            f"<div style='margin-bottom:24px;'>"
            f"<div style='background:#EFF6FF; border-left:4px solid #3B82F6;"
            f"padding:10px 16px; border-radius:0 8px 8px 0; margin-bottom:12px;'>"
            f"<h3 style='margin:0; color:#1E3A5F; font-size:16px;'>🏭 {industry}</h3>"
            f"</div>"
            + items_html +
            "</div>"
        )

    # AEs del país
    aes_html = ", ".join(aes[:10])
    if len(aes) > 10:
        aes_html += f" y {len(aes) - 10} más"

    html = (
        "<div style='font-family:Arial,sans-serif; max-width:700px;"
        "margin:0 auto; color:#1F2937;'>"

        # Header
        f"<div style='background:linear-gradient(120deg,#003A8C,#0057D9);"
        f"color:white; padding:28px 32px; border-radius:14px 14px 0 0;'>"
        f"<div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>"
        f"<div style='background:#fff; color:#0057D9; border-radius:6px;"
        f"font-weight:700; padding:6px 10px; font-size:16px;'>SAP</div>"
        f"<span style='opacity:.85; font-size:14px;'>Operations Team</span>"
        f"</div>"
        f"<h1 style='margin:0; font-size:28px;'>{flag} Newsletter Semanal - {display_name}</h1>"
        f"<p style='margin:6px 0 0 0; opacity:.85; font-size:14px;'>"
        f"Edición: {today} &nbsp;|&nbsp; {total_news} noticias de cuentas nuevas"
        f"</p>"
        f"</div>"

        # Body
        "<div style='padding:24px; background:#fff; border:1px solid #DBEAFE;"
        "border-top:none; border-radius:0 0 14px 14px;'>"

        f"<p style='color:#374151; font-size:15px; margin-bottom:20px;'>"
        f"Estimado equipo comercial de {display_name},<br><br>"
        f"A continuación encontrarán noticias relevantes de <b>empresas nuevas</b> "
        f"(no incluidas en nuestro portafolio actual) organizadas por industria. "
        f"Estas representan oportunidades de prospección para el equipo.</p>"

        f"<p style='color:#6B7280; font-size:13px; margin-bottom:20px;'>"
        f"<b>AEs del país:</b> {aes_html}</p>"

        "<hr style='border:none; border-top:2px solid #DBEAFE; margin:20px 0;'>"

        + sections_html +

        # Footer
        "<hr style='border:none; border-top:2px solid #DBEAFE; margin:20px 0;'>"
        f"<div style='background:#F8FBFF; border-radius:10px; padding:16px 20px;'>"
        f"<p style='margin:0; font-size:13px; color:#6B7280;'>"
        f"Este newsletter fue generado con asistencia de IA por <b>{sender_name}</b>.<br>"
        f"Las noticias provienen de Google News (fuentes reales). "
        f"El análisis ejecutivo es generado por IA y debe validarse.<br>"
        f"<span style='color:#9CA3AF;'>SAP Operations Team · {today}</span>"
        f"</p>"
        f"</div>"

        "</div>"  # cierre body
        "</div>"  # cierre contenedor principal
    )

    return html


def build_plain_text_newsletter(
    country: str,
    news_by_industry: Dict[str, List[Dict]],
    deep_content: Dict[str, str],
    sender_name: str,
    aes: List[str]
) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    flag = COUNTRY_FLAGS.get(country, "🌎")
    display_name = COUNTRY_DISPLAY.get(country, country)

    lines = []
    lines.append("=" * 60)
    lines.append(f"SAP OPERATIONS TEAM - NEWSLETTER SEMANAL")
    lines.append(f"{flag} {display_name.upper()}")
    lines.append(f"Edición: {today}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Estimado equipo comercial de {display_name},")
    lines.append("")
    lines.append(
        "A continuación las noticias más relevantes de CUENTAS NUEVAS "
        "(no incluidas en nuestro portafolio actual) organizadas por industria."
    )
    lines.append("")
    lines.append(f"AEs del país: {', '.join(aes[:10])}")
    lines.append("")

    for industry in sorted(news_by_industry.keys()):
        items = news_by_industry[industry]
        if not items:
            continue

        lines.append("-" * 60)
        lines.append(f"🏭 {industry.upper()}")
        lines.append("-" * 60)

        for i, item in enumerate(items, 1):
            lines.append(f"\n{i}. {item['title']}")
            lines.append(f"   Fuente: {item['source']} | {item.get('date', '')}")
            lines.append(f"   Link: {item['url']}")

            key = f"{country}_{industry}_{item['title'][:50]}"
            deep = deep_content.get(key, "")
            if deep:
                lines.append("")
                for l in deep.split("\n"):
                    if l.strip():
                        lines.append(f"   {l.strip()}")

        lines.append("")

    lines.append("=" * 60)
    lines.append(f"Generado por: {sender_name}")
    lines.append(f"SAP Operations Team · {today}")
    lines.append("=" * 60)

    return "\n".join(lines)


# =========================
# Mailto para Outlook
# =========================
def build_mailto_link(
    to_emails: List[str],
    cc_emails: List[str],
    subject: str,
    body_plain: str
) -> str:
    to = ";".join(to_emails)
    cc = ";".join(cc_emails)
    subject_enc = urllib.parse.quote(subject)
    body_enc = urllib.parse.quote(body_plain[:8000])
    return f"mailto:{to}?cc={cc}&subject={subject_enc}&body={body_enc}"


# =========================
# SESSION STATE
# =========================
if "territory_data" not in st.session_state:
    st.session_state.territory_data = load_territory_data()
if "selected_country" not in st.session_state:
    st.session_state.selected_country = None
if "country_info" not in st.session_state:
    st.session_state.country_info = None
if "headlines_by_industry" not in st.session_state:
    st.session_state.headlines_by_industry = {}
if "selected_news_by_industry" not in st.session_state:
    st.session_state.selected_news_by_industry = {}
if "deep_content" not in st.session_state:
    st.session_state.deep_content = {}
if "newsletter_html" not in st.session_state:
    st.session_state.newsletter_html = ""
if "newsletter_plain" not in st.session_state:
    st.session_state.newsletter_plain = ""
if "phase" not in st.session_state:
    st.session_state.phase = 1
if "search_completed" not in st.session_state:
    st.session_state.search_completed = False


# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")

    sender_name = st.text_input(
        "Tu nombre",
        value="Equipo de Operaciones SAP",
        help="Aparecerá en la firma del newsletter"
    )

    st.markdown("---")
    st.markdown("### 🌎 Seleccionar País")

    country_options = {
        "🇦🇷 Argentina": "ARGENTINA",
        "🇨🇱 Chile": "CHILE",
        "🇵🇪 Perú": "PERU",
        "🇨🇴 Colombia": "COLOMBIA"
    }

    selected_display = st.radio(
        "País para el newsletter:",
        options=list(country_options.keys()),
        index=0
    )
    selected_country = country_options[selected_display]

    # Cargar datos del país
    if selected_country != st.session_state.selected_country:
        st.session_state.selected_country = selected_country
        st.session_state.country_info = get_country_data(
            st.session_state.territory_data, selected_country
        )
        # Reset phases
        st.session_state.headlines_by_industry = {}
        st.session_state.selected_news_by_industry = {}
        st.session_state.deep_content = {}
        st.session_state.newsletter_html = ""
        st.session_state.newsletter_plain = ""
        st.session_state.search_completed = False
        st.session_state.phase = 1

    country_info = st.session_state.country_info

    if country_info:
        st.markdown("---")
        st.markdown("### 📊 Datos del País")
        st.metric("Account Executives", len(country_info["aes"]))
        st.metric("Industrias", len(country_info["industries"]))
        st.metric("Cuentas existentes", len(country_info["all_entities"]))

        with st.expander("👥 AEs del país"):
            for ae in country_info["aes"]:
                email = AE_EMAILS.get(ae, "")
                if email:
                    st.markdown(f"- **{ae}** · `{email}`")
                else:
                    st.markdown(f"- **{ae}**")

        with st.expander("🏭 Industrias"):
            for ind in country_info["industries"]:
                count = len(country_info["entities_by_industry"].get(ind, []))
                st.markdown(f"- {ind} ({count} cuentas)")

    st.markdown("---")
    st.markdown("### 📧 Con copia (CC)")
    active_cc = []
    for email in CC_EMAILS:
        if st.checkbox(email, value=True, key=f"cc_{email}"):
            active_cc.append(email)

    st.markdown("---")
    st.caption("💡 API Key: configura `ANTHROPIC_API_KEY` en Streamlit Secrets")


# =========================
# FASE 1 · Seleccionar industrias y buscar
# =========================
if country_info:
    display_name = COUNTRY_DISPLAY.get(selected_country, selected_country)
    flag = COUNTRY_FLAGS.get(selected_country, "🌎")

    st.markdown(
        f"<div class='step-header'>📡 Paso 1 · Buscar noticias de cuentas nuevas "
        f"en {flag} {display_name}</div>",
        unsafe_allow_html=True
    )

    # Selección de industrias
    st.markdown("**Selecciona las industrias para buscar noticias:**")

    selected_industries = []
    cols = st.columns(3)
    for i, ind in enumerate(country_info["industries"]):
        col_idx = i % 3
        with cols[col_idx]:
            count = len(country_info["entities_by_industry"].get(ind, []))
            if st.checkbox(f"{ind} ({count})", value=True, key=f"ind_sel_{ind}"):
                selected_industries.append(ind)

    st.markdown("---")

    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(
            f"Se buscarán noticias de **empresas que NO están** en las "
            f"**{len(country_info['all_entities'])} cuentas existentes** del país. "
            f"Máximo 10 noticias por industria."
        )
    with col_btn:
        buscar = st.button(
            "🔍 Buscar Noticias",
            type="primary",
            use_container_width=True,
            disabled=not selected_industries
        )

    if buscar:
        st.session_state.headlines_by_industry = {}
        st.session_state.selected_news_by_industry = {}
        st.session_state.deep_content = {}
        st.session_state.newsletter_html = ""
        st.session_state.newsletter_plain = ""

        progress = st.progress(0, text="Iniciando búsqueda...")
        total_ind = len(selected_industries)

        for i, industry in enumerate(selected_industries):
            pct = int((i / total_ind) * 100)
            progress.progress(pct, text=f"Buscando: {industry}...")

            existing = country_info["entities_by_industry"].get(industry, set())
            if isinstance(existing, list):
                existing = set(existing)

            news = search_industry_news(
                industry=industry,
                country=selected_country,
                existing_entities=existing,
                max_results=10
            )

            if news:
                st.session_state.headlines_by_industry[industry] = news

        progress.progress(100, text="✅ Búsqueda completada")
        st.session_state.search_completed = True
        st.session_state.phase = 2
        st.rerun()


# =========================
# FASE 2 · Selección de noticias
# =========================
if st.session_state.search_completed and st.session_state.headlines_by_industry:
    display_name = COUNTRY_DISPLAY.get(selected_country, selected_country)
    flag = COUNTRY_FLAGS.get(selected_country, "🌎")

    total_found = sum(len(v) for v in st.session_state.headlines_by_industry.values())
    industries_with_news = len(st.session_state.headlines_by_industry)

    st.markdown(
        f"<div class='step-header'>✅ Paso 2 · Selecciona noticias para el newsletter "
        f"({total_found} encontradas en {industries_with_news} industrias)</div>",
        unsafe_allow_html=True
    )

    total_selected = 0

    for industry in sorted(st.session_state.headlines_by_industry.keys()):
        news_list = st.session_state.headlines_by_industry[industry]
        if not news_list:
            continue

        # Header de industria
        aes_in_industry = country_info["aes_by_industry"].get(industry, [])
        aes_str = ", ".join(aes_in_industry[:5])
        if len(aes_in_industry) > 5:
            aes_str += f" +{len(aes_in_industry) - 5}"

        st.markdown(
            f"<div class='industry-header'>"
            f"🏭 {industry} "
            f"<span style='font-weight:400; font-size:12px; color:#6B7280;'>"
            f"({len(news_list)} noticias · AEs: {aes_str})</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        for idx, item in enumerate(news_list):
            key_cb = f"sel_{industry}_{idx}"

            col_check, col_info = st.columns([0.5, 9.5])

            with col_check:
                selected = st.checkbox("", key=key_cb, label_visibility="collapsed")

            with col_info:
                summary_text = ""
                if item.get("summary"):
                    summary_text = (
                        f"<p style='color:#4B5563; font-size:12px; margin-top:6px; "
                        f"font-style:italic;'>{item['summary'][:150]}...</p>"
                    )

                st.markdown(
                    f"<div class='news-card'>"
                    f"<div style='font-weight:600; color:#1E3A5F; font-size:14px;'>"
                    f"{item['title']}</div>"
                    f"<div style='color:#6B7280; font-size:12px; margin-top:4px;'>"
                    f"📰 {item['source']} &nbsp;|&nbsp; "
                    f"📅 {item.get('date', 'Reciente')} &nbsp;|&nbsp; "
                    f"<a href='{item['url']}' target='_blank' "
                    f"style='color:#3B82F6;'>Ver fuente ↗</a>"
                    f"</div>"
                    f"{summary_text}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            if selected:
                total_selected += 1
                if industry not in st.session_state.selected_news_by_industry:
                    st.session_state.selected_news_by_industry[industry] = []
                titles_in = [
                    n['title']
                    for n in st.session_state.selected_news_by_industry[industry]
                ]
                if item['title'] not in titles_in:
                    st.session_state.selected_news_by_industry[industry].append(item)
            else:
                if industry in st.session_state.selected_news_by_industry:
                    st.session_state.selected_news_by_industry[industry] = [
                        n for n in st.session_state.selected_news_by_industry[industry]
                        if n['title'] != item['title']
                    ]

        st.markdown("---")

    # Botón generar
    if total_selected > 0:
        st.info(
            f"📌 **{total_selected} noticia(s) seleccionada(s)**. "
            f"Haz clic en 'Generar Newsletter' para que la IA profundice cada una."
        )

        st.markdown(
            "<div class='step-header'>🤖 Paso 3 · Generar Newsletter con análisis IA</div>",
            unsafe_allow_html=True
        )

        col_gen1, col_gen2 = st.columns([2, 1])
        with col_gen1:
            st.markdown(
                "La IA analizará cada noticia seleccionada y generará un análisis "
                "ejecutivo con contexto, impacto B2B y oportunidades SAP."
            )
        with col_gen2:
            generar = st.button(
                "🚀 Generar Newsletter",
                type="primary",
                use_container_width=True
            )

        if generar:
            progress = st.progress(0, text="Iniciando análisis con IA...")

            all_items = []
            for industry, items in st.session_state.selected_news_by_industry.items():
                for item in items:
                    all_items.append((industry, item))

            total = len(all_items)

            for i, (industry, item) in enumerate(all_items):
                pct = int((i / total) * 100)
                progress.progress(
                    pct,
                    text=f"Analizando ({i+1}/{total}): {item['title'][:50]}..."
                )

                key = f"{selected_country}_{industry}_{item['title'][:50]}"
                if key not in st.session_state.deep_content:
                    deep = deepen_news_item(
                        title=item['title'],
                        source=item['source'],
                        industry=industry,
                        country=COUNTRY_DISPLAY.get(selected_country, selected_country)
                    )
                    st.session_state.deep_content[key] = deep

            progress.progress(100, text="✅ Análisis completado. Generando newsletter...")

            st.session_state.newsletter_html = build_full_newsletter_html(
                country=selected_country,
                news_by_industry=st.session_state.selected_news_by_industry,
                deep_content=st.session_state.deep_content,
                sender_name=sender_name,
                aes=country_info["aes"]
            )
            st.session_state.newsletter_plain = build_plain_text_newsletter(
                country=selected_country,
                news_by_industry=st.session_state.selected_news_by_industry,
                deep_content=st.session_state.deep_content,
                sender_name=sender_name,
                aes=country_info["aes"]
            )
            st.session_state.phase = 3
            st.rerun()
    else:
        st.warning("☝️ Selecciona al menos una noticia para continuar.")


# =========================
# FASE 3 · Preview y envío
# =========================
if st.session_state.newsletter_html:
    display_name = COUNTRY_DISPLAY.get(selected_country, selected_country)
    flag = COUNTRY_FLAGS.get(selected_country, "🌎")

    st.markdown(
        f"<div class='step-header'>📧 Paso 4 · Preview y envío - "
        f"{flag} {display_name}</div>",
        unsafe_allow_html=True
    )

    tab_preview, tab_html, tab_plain = st.tabs(
        ["👁️ Vista previa", "🔤 HTML", "📄 Texto plano"]
    )

    with tab_preview:
        st.markdown(
            "<div style='border:2px solid #BFDBFE; border-radius:14px; overflow:hidden; "
            "margin-top:12px;'>" +
            st.session_state.newsletter_html +
            "</div>",
            unsafe_allow_html=True
        )

    with tab_html:
        st.code(st.session_state.newsletter_html, language="html")
        st.download_button(
            label="⬇️ Descargar HTML",
            data=st.session_state.newsletter_html,
            file_name=f"newsletter_sap_{display_name}_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html"
        )

    with tab_plain:
        st.text_area(
            "Texto plano del newsletter",
            value=st.session_state.newsletter_plain,
            height=400
        )
        st.download_button(
            label="⬇️ Descargar TXT",
            data=st.session_state.newsletter_plain,
            file_name=f"newsletter_sap_{display_name}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

    # --- Sección de envío ---
    st.markdown("---")
    st.markdown(f"### 📤 Enviar por Outlook - {flag} {display_name}")

    # Obtener emails de AEs del país
    ae_emails_for_country = []
    for ae in country_info["aes"]:
        email = AE_EMAILS.get(ae, "")
        if email:
            ae_emails_for_country.append(email)

    col_mail1, col_mail2 = st.columns(2)

    with col_mail1:
        st.markdown("**Destinatarios (Para) - AEs del país:**")
        selected_to = []
        for email in ae_emails_for_country:
            if st.checkbox(email, value=True, key=f"to_send_{email}"):
                selected_to.append(email)

    with col_mail2:
        st.markdown("**Con copia (CC):**")
        for email in active_cc:
            st.markdown(f"- `{email}`")

    # Asunto
    today_str = datetime.now().strftime("%d/%m/%Y")
    total_news_final = sum(
        len(v) for v in st.session_state.selected_news_by_industry.values()
    )
    default_subject = (
        f"SAP Newsletter Semanal · {display_name} · {today_str} · "
        f"{total_news_final} noticias - Cuentas Nuevas"
    )

    email_subject = st.text_input(
        "✏️ Asunto del correo",
        value=default_subject,
        help="Puedes editar el asunto antes de abrir Outlook"
    )

    st.markdown("""
    <div style='background:#EFF6FF; border:1px solid #BFDBFE; color:#1E40AF;
                padding:12px 16px; border-radius:10px; margin:12px 0; font-size:13px;'>
        <b>💡 Opciones de envío:</b><br>
        - <b>Opción A:</b> Abre Outlook con texto plano (compatibilidad máxima).<br>
        - <b>Opción B:</b> Descarga HTML, ábrelo en navegador, copia y pega en Outlook
          para formato visual completo.
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if selected_to:
            mailto_link = build_mailto_link(
                to_emails=selected_to,
                cc_emails=active_cc,
                subject=email_subject,
                body_plain=st.session_state.newsletter_plain
            )
            st.markdown(
                f"<a href='{mailto_link}' "
                f"style='display:block; text-align:center; background:#0078D4; "
                f"color:white; padding:12px 20px; border-radius:10px; "
                f"text-decoration:none; font-weight:700; font-size:14px; "
                f"box-shadow:0 4px 14px rgba(0,120,212,.35);'>"
                f"📧 Abrir en Outlook</a>",
                unsafe_allow_html=True
            )
        else:
            st.button("📧 Abrir en Outlook", disabled=True)
            st.caption("Selecciona al menos un destinatario.")

    with col_btn2:
        st.download_button(
            label="⬇️ Descargar HTML",
            data=st.session_state.newsletter_html,
            file_name=f"newsletter_{display_name}_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True
        )

    with col_btn3:
        if st.button(
            "🔄 Nuevo Newsletter",
            use_container_width=True,
            help="Limpia todo y comienza desde cero"
        ):
            for key in [
                "headlines_by_industry", "selected_news_by_industry",
                "deep_content"
            ]:
                st.session_state[key] = {}
            st.session_state.newsletter_html = ""
            st.session_state.newsletter_plain = ""
            st.session_state.search_completed = False
            st.session_state.phase = 1
            st.rerun()

    # --- Instrucciones HTML en Outlook ---
    with st.expander("📋 ¿Cómo pegar el HTML con formato en Outlook?"):
        st.markdown("""
        **Pasos para enviar con formato visual completo:**

        1. Haz clic en **⬇️ Descargar HTML** para guardar el archivo.
        2. Abre el archivo `.html` en tu navegador (Chrome, Edge, Firefox).
        3. Selecciona todo: `Ctrl + A`
        4. Copia: `Ctrl + C`
        5. Abre un **nuevo correo en Outlook**.
        6. Pega: `Ctrl + V` en el cuerpo del mensaje.
        7. Completa destinatarios y asunto.
        8. ¡Envía! 🚀

        > **Tip:** Asegúrate de que Outlook esté en modo **HTML**
        > (no texto plano) para conservar el formato.
        """)

    # --- Resumen final ---
    st.markdown("---")
    st.markdown(f"### 📊 Resumen del Newsletter - {flag} {display_name}")

    summary_cols = st.columns(3)
    with summary_cols[0]:
        st.metric("Total noticias", total_news_final)
    with summary_cols[1]:
        st.metric(
            "Industrias cubiertas",
            len([v for v in st.session_state.selected_news_by_industry.values() if v])
        )
    with summary_cols[2]:
        st.metric("AEs destinatarios", len(selected_to) if selected_to else 0)

    # Detalle por industria
    for industry in sorted(st.session_state.selected_news_by_industry.keys()):
        items = st.session_state.selected_news_by_industry[industry]
        if not items:
            continue

        with st.expander(f"🏭 {industry} · {len(items)} noticia(s)"):
            for item in items:
                key = f"{selected_country}_{industry}_{item['title'][:50]}"
                deep = st.session_state.deep_content.get(key, "")

                st.markdown(
                    f"<div style='border:1px solid #DBEAFE; border-radius:10px;"
                    f"padding:14px 16px; margin-bottom:10px; background:#F8FBFF;'>"
                    f"<b style='color:#1E3A5F;'>{item['title']}</b><br>"
                    f"<span style='color:#6B7280; font-size:12px;'>"
                    f"📰 {item['source']} | 📅 {item.get('date', 'Reciente')} | "
                    f"<a href='{item['url']}' target='_blank' "
                    f"style='color:#3B82F6;'>Ver fuente ↗</a>"
                    f"</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

                if deep:
                    with st.expander("Ver análisis ejecutivo", expanded=False):
                        st.markdown(deep)

else:
    if not st.session_state.search_completed and not st.session_state.headlines_by_industry:
        st.markdown("---")
        st.info(
            "👈 Selecciona un país en el sidebar y haz clic en "
            "'🔍 Buscar Noticias' para comenzar."
        )


# =========================
# Footer
# =========================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#9CA3AF; font-size:12px; padding:10px 0;'>"
    "SAP Operations Team · Newsletter Intelligence · "
    "Noticias reales via Google News RSS · Análisis por Claude AI (Anthropic) · "
    + datetime.now().strftime("%Y") +
    "</div>",
    unsafe_allow_html=True
)
