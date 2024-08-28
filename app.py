from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

CSV_BASE_PATH = 'data/'

CATEGORIES_MAP = {"Conf&DataDiscl":"Confidentiality and Data Disclosure", 
              "Rights":"People Rights", 
              "Adoption": "Adoption",
              "ServiceQuality": "Service Quality",
              "Law&Compliance": "Laws, Regulations, Compliance",
              "Technical": "Technical",
              "Security":"Security",
              "Privacy": "Privacy",
              "Trust": "Trust",
              "SysDesign": "System Design",
              "Governance&Procedures": "Governance Actors, Management, and Procedures",
              "Management": "Governance Actors, Management, and Procedures",
              "Socio-political": "Social and Political",
              "Functional": "Functional Requirement",
              "Integr": "Integrity",
              "Avail": "Availability",
              "Transp": "Transparency",
              "Surv": "Surveillance",
              "Authn&Authz": "Authenticity of Data and Identity, Authorization",
              "Abuse": "Abuse of system functionality"
              }

def rename_columns(df):
    global CATEGORIES_MAP
    return df.rename(columns=CATEGORIES_MAP)

SPECIFIC_ENTITY = None
SPECIFIC_DEF = None

def get_categories(df):
    tmp = set(df.columns)
    tmp.discard('Name')
    tmp.discard('Threats')
    tmp.discard('Requirements')
    tmp.discard('Mitigations')
    tmp.discard('Goals')
    return tmp

def cleanup_df(df,entity):
    if entity == "Requirements":
        return df.drop(labels=['References','Description','Addresses'], axis=1)
    elif entity == "Threats":
        return df.drop(labels=['References','Description','Security','Privacy','STRIDE','LINDDUN','Origin'], axis=1)
    elif entity == "Mitigations":
        return df.dropna(axis=1)


def simplify_table(df,entity):
    simplified_df = pd.DataFrame()
    simplified_df[entity] = df[entity]

    categories = get_categories(df)

    df["name_index"] = df[entity]
    df = df.set_index("name_index")
    
    cats = []
    for cur_name in df[entity]:
        tmp = []
        for cat in categories:
            if df.at[cur_name,cat] == 'T':
                tmp.append(cat)
        cats.append(tmp)
    simplified_df["Categories"] = cats

    df = df.reset_index().drop(labels=['name_index'],axis=1)
    # simplified_df = simplified_df.reset_index().set_index("index")
    simplified_df = simplified_df.reset_index().drop(labels=['index'], axis=1)
    return simplified_df

def read_and_cleanup(entity):
    df = pd.read_csv(CSV_BASE_PATH + entity + ".csv")
    df = df.reset_index().set_index("index").reset_index()
    df.drop(labels=['index'], axis=1, inplace=True)
    df = cleanup_df(df,entity)
    return df


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_table', methods=['GET'])
def get_table():
    entity = request.args.get("entity")

    df = read_and_cleanup(entity)

    df = simplify_table(df,entity)

    return jsonify(table_html=df.to_html(classes='data-table', index=False, index_names=False))

@app.route('/specific', methods=['GET'])
def specific():
    return render_template('specific.html')

@app.route('/set_specific', methods=['GET'])
def set_specific():
    global SPECIFIC_ENTITY
    global SPECIFIC_DEF 
    SPECIFIC_ENTITY = request.args.get("entity")
    SPECIFIC_DEF = request.args.get("def")
    return "ok"

def build_connections_table(name,definition):

    main_df = read_and_cleanup(name)
    if name == 'Requirements':
        df2 = read_and_cleanup("Mitigations")
    elif name == 'Mitigations':
        df2 = read_and_cleanup("Requirements")
    else:
        df2 = read_and_cleanup("Threats")

    # find specific row in main df
    row = main_df[main_df[name] == definition].reset_index()

    # interesect the categories between the two dfs
    selected_cats = set()
    # extract categories from the extracted row
    for cat in get_categories(main_df).intersection(get_categories(df2)):
        if row.at[0,cat] == 'T':
            selected_cats.add(cat)

    # select all rows in df2 that match the signature of the interesected categories
    mask = pd.Series([True] * len(df2))
    
    for col in selected_cats:
        mask &= df2[col].isin(['T'])

    return rename_columns(df2[mask])

@app.route('/get_specific', methods=['GET'])
def get_specific():
    global SPECIFIC_DEF
    global SPECIFIC_ENTITY
    
    if (SPECIFIC_DEF is not None) and (SPECIFIC_ENTITY is not None):

        df = read_and_cleanup(SPECIFIC_ENTITY)
        starting_record = df[df[SPECIFIC_ENTITY] == SPECIFIC_DEF]
        # print(starting_record)

        df = build_connections_table(name=SPECIFIC_ENTITY,definition=SPECIFIC_DEF)
        # df = pd.read_csv(CSV_BASE_PATH + SPECIFIC_ENTITY + ".csv")
        
        # df = df.reset_index().set_index("index")
        # df = cleanup_df(df,SPECIFIC_ENTITY)
        # return jsonify(table_html=df.to_html(classes='data-table', index=False, index_names=False))
    else:
        starting_record = None
        df = pd.read_csv(CSV_BASE_PATH + "Requirements" + ".csv")
        df = df.reset_index().set_index("index")
        df = cleanup_df(df,"Requirements")

    mitigations_html = df.to_html(classes='data-table', index=False, index_names=False)
    requirements_html = df.to_html(classes='data-table', index=False, index_names=False)

    # requirements -> mitigations
    # mitigations -> requirements & threats
    # threats -> mitigations
    abc = ['ciao0','ciao1','ciao2']
    entities = ['Mitigations']
    table_html=df.to_html(classes='data-table', index=False, index_names=False)
    tables = [table_html]

    return jsonify(entity=SPECIFIC_ENTITY,
                    starting_record=starting_record.to_html(classes='data-table', index=False, index_names=False),
                    table_html=df.to_html(classes='data-table', index=False, index_names=False),
                    abc=abc,
                    entities=entities,
                    tables=tables)
    

if __name__ == '__main__':
    app.run(debug=True)