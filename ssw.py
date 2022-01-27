import requests, os, csv, time, random, pandas as pd
from bs4 import BeautifulSoup
from datetime import date, datetime

class SSW:
    def __init__(self, domain, cpf, user, password):
        self.domain = domain
        self.cpf = cpf
        self.user = user
        self.password = password
        self.header = self.LoginSSW(self.domain, self.cpf, self.user, self.password)
    def LoginSSW(self, dominio, cpf, Usuario, Senha, tokenBoolen=False):
        login = requests.post("https://sistema.ssw.inf.br/bin/ssw0422", data={
            "act": "L",
            "f1": dominio,
            "f2": cpf,
            "f3": Usuario,
            "f4": Senha,
            "f6": "TRUE"
        }, headers={
            "Accept": "*/*",
            "Content-type": "application/x-www-form-urlencoded",
            "Cookie": f"remember=1; sigla_emp={dominio}; ssw4importa=S; ssw0197_seq_cliente=; useri={cpf}; ssw_dom={dominio}",
            "Host": "sistema.ssw.inf.br",
            "Origin": "https://sistema.ssw.inf.br",
            "Referer": "https://sistema.ssw.inf.br/bin/ssw0422",
        })
        cookie = login.cookies
        token = cookie._cookies['.sistema.ssw.inf.br']['/']['token'].value
        chave = cookie._cookies['sistema.ssw.inf.br']['/bin']['chave'].value
        header = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Content-type": "application/x-www-form-urlencoded",
            "Cookie": f"remember=1; sigla_emp={dominio}; ssw4importa=S; ssw0197_seq_cliente=; useri={cpf}; login={Usuario}; chave={chave}; ssw_dom={dominio}; token={token}"
        }
        if tokenBoolen: return token, header
        return header
    def get_plates_list(self):
        veic = []
        data = {'act': 'ENV', 'tp_prop': 'T', 'disponivel': 'T', 'rastreado': 'T', 'tp_rel': 'S', 'web_body': ''}
        resposta = requests.post("https://sistema.ssw.inf.br/bin/ssw0043", data=data, headers=self.header)
        dummy = BeautifulSoup(resposta.content, "html.parser").contents[0].attrs['value'][11:17+len(list(self.user))]
        veiculos = requests.get(f"https://sistema.ssw.inf.br/bin/ssw0424?act={dummy}ssw0043.html&filename=ssw0043a.sswweb&path=&down=1&nw=1", headers=self.header)

        for i,line in enumerate(veiculos.text.split("\n")):
            lineList = line.split(";")
            if len(lineList) > 2 and i != 0:
                veic.append(lineList[1])
        return veic
    def get_drivers_list(self):
        mot = []
        data = {'act': 'IMP', 'f1': 'T', 'f2': 'T', 'f13': 's'}
        resposta = requests.post("https://sistema.ssw.inf.br/bin/ssw0067", data=data, headers=self.header)
        dummy = BeautifulSoup(resposta.content, "html.parser").contents[0].attrs['value'][14:20+len(list(self.user))]
        motoristas = requests.get(
            f"https://sistema.ssw.inf.br/bin/ssw0424?act={dummy}ssw0062.html&filename=CSVmotoristas.sswweb&path=&down=1&nw=1", 
            headers=self.header
        )
        for i,line in enumerate(motoristas.text.split("\n")):
            lineList = line.split(";")
            if len(lineList) > 2 and i != 0:
                mot.append(lineList[2])
        return mot
    def returns(self, notas:list):
        data_atual = date.today()
        data_atual_ano = int(data_atual.year)
        data_atual_mes = int(data_atual.month)
        data_atual_dia = int(data_atual.day)
        if data_atual_mes < 10:
            data_atual_mes = "0" + str(data_atual_mes)
        if data_atual_dia < 10:
            data_atual_dia = "0" + str(data_atual_dia)
        list_data_atual_ano = list(str(data_atual_ano))
        data_atual_ano = str(list_data_atual_ano[2]) + str(list_data_atual_ano[3])
        data_atual = str(data_atual_dia) + str(data_atual_mes) + str(data_atual_ano)

        data_e_hora_atuais = datetime.now()
        data_e_hora_em_texto = data_e_hora_atuais.strftime('%H%M')

        for nota in notas:
            payload = {
                "act": "P2",
                "t_nro_nf": str(nota),
                "t_data_ini": "300620",
                "t_data_fin": f"{data_atual}",
                "data_ini_inf": "30/12/99",
                "data_fin_inf": "30/12/99",
                "seq_ctrc": "0",
                "local": "",
                "FAMILIA": ""
            }
            resposta = requests.post("https://sistema.ssw.inf.br/bin/ssw0053", data=payload, headers=self.header)
            soup = BeautifulSoup(resposta.content, "html.parser")
            var = soup.select(".texto")[3].text
            var = str(int(var))
            payload = {
                'act': 'II3',
                'f3': '31',
                'f4': f"{data_atual}",
                'f5': f'{data_e_hora_em_texto}',
                'f8': 'N',
                'f11': 'N',
                'detalhe_oco': '',
                'detalhe_ins': '',
                'tipoFoto': 'avaria',
                'nomeFoto': 'ONHOWNV',
                'extraFoto': 'VIX/2109/30',
                'nomeFotoUsed': '',
                'seq_ctrc': var
            }
            requests.post("https://sistema.ssw.inf.br/bin/ssw0122", headers=self.header, data=payload)
    def to_extract(self, source : str):
        arquivo = pd.read_excel(source)
        notas = []
        for linha in arquivo["NACIONAL LOGISTICA - FRISA              "]:
            try: notas.append(int(linha))
            except: pass
        prim_linha = arquivo["NACIONAL LOGISTICA - FRISA              "][0]
        placa = prim_linha.split(":")[1][1:4] + prim_linha.split(":")[1][5:]
        trat_motorista = arquivo["NACIONAL LOGISTICA - FRISA              "][1]
        nome_motorista = trat_motorista[11:].split("/")[0]
        Total_Notas = ""
        for i in list(linha):
            try: Total_Notas += str(int(i))
            except: pass
        return placa, Total_Notas, nome_motorista, notas
    def BaixaVeiculo(self, placa : str):
        def search(lista, valor):
            return [[lista.index(x), x.index(valor)] for x in lista if valor in x]
        data = {'act': 'ENV', 'tp_prop': 'T', 'disponivel': 'T', 'rastreado': 'T', 'tp_rel': 's'}
        dados = requests.post("https://sistema.ssw.inf.br/bin/ssw0043", headers=self.header, data=data)
        soup = BeautifulSoup(dados.content, "html.parser")
        c = soup.currentTag.currentTag.contents[0].attrs['value']
        url_download = f"https://sistema.ssw.inf.br/bin/ssw0424?act={c[11:31]}.html&filename=CSVssw0043a.sswweb&path=&down=1&nw=1"
        download = requests.get(url_download, headers=self.header)
        t1 = f"{time.time()}{random.random()}"
        with open(f".\{t1}.csv", "wb") as veiculos:
            veiculos.write(download.content)
        with open(f".\{t1}.csv", "r") as csvfile:
            ler = csv.reader(csvfile)
            for i in ler:
                linha = (f"{i[0]+i[-1]}").split(";")
                busc = search(linha, placa)
                if len(busc) > 0: break
        os.remove(f".\{t1}.csv")
        return linha[22], linha[23]
    def BaixaMotorista(self, var : str):
        def busca(busca):
            cpf = None
            t1 = f"{time.time()}{random.random()}"
            with open(f".\{t1}.csv", "wb") as csvf:
                csvf.write(csv_wb.content)
            with open(f".\{t1}.csv", "r") as csvfile:
                ler = csv.reader(csvfile, delimiter=";")
                for i in ler:
                    if busca in i:
                        cpf = i[1]
                        break
            os.remove(f".\{t1}.csv")
            return cpf
        data = {'act': 'IMP','f1': 'T','f2': 'T','f13': 's','web_body': ''}
        resposta = requests.post("https://sistema.ssw.inf.br/bin/ssw0067", headers=self.header, data=data)
        soup = BeautifulSoup(resposta.content, "html.parser")
        vaz = ""
        for i in list(soup.currentTag.currentTag.contents[0].attrs['value'])[14:34]: vaz += i
        url_csv = f"https://sistema.ssw.inf.br/bin/ssw0424?act={vaz}.html&filename=CSVmotoristas.sswweb&path=&down=1&nw=1"
        csv_wb = requests.get(url_csv, headers=self.header)
        return busca(var)
    def generate_romane(self, placa, motorista : str, notas : list):
        token, header = self.LoginSSW(tokenBoolen=True)
        cpf_motorista = self.BaixaMotorista(motorista)
        nome_completo_motorista = motorista
        nome_proprietario, cnpj_proprietario = self.BaixaVeiculo(placa)
        cont = 0
        for i in notas:
            cont += 1
            url_desapontar = f"https://sistema.ssw.inf.br/bin/ssw0197?act=SLV&f1=1&answer=S&f2={i}&f3=undefined&f4=undefined&placa={placa}&fil1=&fil2=&fil3=&fil4=&fil5=&fil6=&fil7=&fil8=&fil9=&fil10=&sel_opcao=N&prioritario=N&tem_feriado="
            requests.get(url_desapontar, headers=header)
            url_035 = f"https://sistema.ssw.inf.br/bin/ssw0197?act=SLV&f1=1&f2={i}&f3=undefined&f4=undefined&placa={placa}&fil1=&fil2=&fil3=&fil4=&fil5=&fil6=&fil7=&fil8=&fil9=&fil10=&sel_opcao=N&prioritario=N&tem_feriado="
            requests.get(url_035, headers=header)
        dados = requests.post("https://sistema.ssw.inf.br/bin/ssw0197", data = {
            'act': 'NFS',
            'nova_placa': 'S',
            'placa_provisoria': f'{placa}',
            'entrega_dificil': 'N',
            'prioritario': 'N',
            'tp_carregamento': '',
            'qtde': '0',
            'setcookie': '1'
        }, headers=header)
        soup = BeautifulSoup(dados.content, "html.parser")
        qtde = soup.select("#c1l1")[0].attrs['value']
        peso = soup.select("#c2l1")[0].attrs['value']
        vlr_merc = soup.select("#c5l1")[0].attrs['value']
        rom = requests.post("https://sistema.ssw.inf.br/bin/ssw0197", data={
            "act": "ROM2",
            "newPage": "S",
            "button_env_enable": 'ROM2',
            "button_env_disable": 'link_env',
            "teste_proprietario": 'ok',
            "ajudante": 'N',
            "forcerom": '',
            "criticas_ciot": '',
            "gr_nivel": '',
            "gr_desc": '',
            "gr_obser": '',
            "gr_codigos": '0|0',
            "gr_informado": '',
            "autorizado_por": '',
            'isca1': '',
            'isca1_nr': '',
            'isca2': '',
            'isca2_nr': '',
            'cnpj_escolta': '',
            'vlr_escolta': '',
            'da_lista': 'S',
            'placa': f'{placa}',
            'sel_opcao': 'N',
            'sel_ent_dif': 'N',
            'prioritario': 'N',
            'seq_cliente': '0',
            'sub1': '',
            'sub2': '',
            'sub3': '',
            'sub4': '',
            'sub5': '',
            'fil1': '',
            'fil2': '',
            'fil3': '',
            'fil4': '',
            'fil5': '',
            'fil6': '',
            'fil7': '',
            'fil8': '',
            'fil9': '',
            'fil10': '',
            'inp_199': 'SERRA/ES',
            'newPage': 'S',
            'button_env_enable': 'ROM2',
            'button_env_disable': 'link_env',
            'teste_proprietario': 'ok',
            'ajudante': 'N',
            'forcerom': '',
            'criticas_ciot': '',
            'gr_nivel': '',
            'gr_desc': '',
            'gr_obser': '',
            'gr_codigos': '0|0',
            'gr_informado': '',
            'autorizado_por': '',
            'isca1': '',
            'isca1_nr': '',
            'isca2': '',
            'isca2_nr': '',
            'cnpj_escolta': '',
            'vlr_escolta': '',
            'da_lista': 'S',
            'placa': f'{placa}',
            'sel_opcao': 'N',
            'sel_ent_dif': 'N',
            'prioritario': 'N',
            'seq_cliente': '0',
            'sub1': '',
            'sub2': '',
            'sub3': '',
            'sub4': '',
            'sub5': '',
            'fil1': '',
            'fil2': '',
            'fil3': '',
            'fil4': '',
            'fil5': '',
            'fil6': '',
            'fil7': '',
            'fil8': '',
            'fil9': '',
            'fil10': '',
            'btn_733': 'N',
            'f2': f'{placa}',
            'prop_cgc': f'{cnpj_proprietario}',
            'prop_nome': f'{nome_proprietario}',
            'tac': 'N',
            'f9': f'{cpf_motorista}',
            'motorista': f'{nome_completo_motorista}',
            'qtde': f'{qtde}',
            'peso': f'{peso}',
            'vlr_merc': f'{vlr_merc}',
            'totveic': f'{vlr_merc}',
            'id_gerar_rom_col': 'N',
            'id_email_dest': 'N',
            'id_itinerante': 'N',
            'remember': '1',
            'ssw4importa': 'S',
            'ssw0197_seq_cliente': '',
            'useri': f'{self.cpf}',
            'ssw_dom': f'{self.domain}',
            'token': token
        }, headers=header)
        soup = BeautifulSoup(rom.content, "html.parser")
        mensagem = soup.contents[0].text
        if len(list(mensagem)) == 0: return "Romaneio Gerado com sucesso!"
        else: return mensagem
    def marked_notes(self, notas : list):
        data_atual = date.today().strftime(r'%d%m%y')
        score = 0
        header = self.header
        for nota in notas:
            resposta = requests.post("https://sistema.ssw.inf.br/bin/ssw0053", data={
                "act": "P2",
                "t_nro_nf": str(int(nota)),
                "t_data_ini": "300620",
                "t_data_fin": str(data_atual),
                "data_ini_inf": "30/12/99",
                "data_fin_inf": "30/12/99",
                "seq_ctrc": "0",
                "local": "",
                "FAMILIA": ""
            }, headers=header)
            soup = BeautifulSoup(resposta.content, "html.parser")
            var = soup.select(".texto")[3].text

            resposta = requests.post("https://sistema.ssw.inf.br/bin/ssw0053", data={
                "ctrc_seq_ctrc": str(int(var)),
                "data_ini_inf": "30/6/20"
            }, headers=header)
            soup = BeautifulSoup(resposta.content, "html.parser")
            cte = soup.select("#chave_cte")[0].attrs['value']

            requests.post("https://sistema.ssw.inf.br/bin/ssw0198", data={
                "act": "BA5",
                "f3": "01",
                "descricao": "MERCADORIA ENTREGUE",
                "f4": f"{data_atual}",
                "f5": f"{cte}",
                "tipo": "S",
                "tipo_tela": "C",
                "tentativa1": "31",
                "tentativa2": "32",
                "tentativa3": "33"
            }, headers=header)
            score += 1
        return {
            "marked_notes": score
        }
