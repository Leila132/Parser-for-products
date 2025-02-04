import pandas as pd
import re
from deep_translator import GoogleTranslator

df_prods = pd.read_excel('/content/Товары магазина.xlsx', header=0)
df_prices = pd.read_excel('/content/Прайсы с телеграма 28.01.xlsx', header=0)

def remove_year_from_string(s):
    pattern = r'\s*\(?\b(20[0-2][0-9])\b\)?\s*$'
    result = re.sub(pattern, '', s).strip()
    return result

def contains_only_digits_and_spaces(s):
    return s.replace(" ", "").isdigit()

def check_keywords_in_strings(str1, str2):
    # Список ключевых слов
    keywords = ["pro", "max", "air", "mini", "xl", "xr", "xs", "plus", "lite", "se", "proplus", "ultra", "pro+", "nfc", "5g"]

    found_keywords_str1 = [word for word in keywords if word in str1.lower()]

    found_keywords_str2 = [word for word in keywords if word in str2.lower()]

    return set(found_keywords_str1) == set(found_keywords_str2)

df_res = pd.DataFrame(columns=["id1", "name1", "id2", "name2", "dict"])
df_res_itog = pd.DataFrame(columns=["id", "name", "p1", "price1", "p2", "price2", "p3", "price3"])

def add_row(id1, name1, id2, name2, dict1):
    global df_res
    new_row = {"id1": id1, "name1": name1, "id2": id2, "name2": name2, "dict": dict1}
    df_res = pd.concat([df_res, pd.DataFrame([new_row])], ignore_index=True)
def add_row_itog(id, name, p, price):
    global df_res_itog
    # Проверяем, есть ли строка с таким id в DataFrame
    if id in df_res_itog["id"].values:
        # Если id уже существует, обновляем существующую строку
        row_index = df_res_itog.index[df_res_itog["id"] == id].tolist()[0]  # Находим индекс строки
        row = df_res_itog.loc[row_index]  # Получаем строку

        # Заполняем p2 и price2, если они пустые
        if pd.isna(row["p2"]):
            df_res_itog.at[row_index, "p2"] = p
            df_res_itog.at[row_index, "price2"] = price
        # Иначе заполняем p3 и price3
        elif pd.isna(row["p3"]):
            df_res_itog.at[row_index, "p3"] = p
            df_res_itog.at[row_index, "price3"] = price
    else:
        # Если id нет, создаём новую строку
        new_row = {
            "id": id,
            "name": name,
            "p1": p,
            "price1": price,
            "p2": None,
            "price2": None,
            "p3": None,
            "price3": None
        }
        # Добавляем новую строку в DataFrame
        df_res_itog = pd.concat([df_res_itog, pd.DataFrame([new_row])], ignore_index=True)

no_words = ["pad", "mini", "se", "x", "lite", "pro", "plus", "5g", "ultra"]

for index, row in df_prods.iterrows():
  if index > -1:
    prod_dict = {}
    #Пробуем получить модель
    models_name = []
    proizv = ""
    try:
      proizv = row[2].strip().lower()
    except:
      pass
    model = remove_year_from_string(row[3].strip().lower())  #Если в конце есть год, то убираем
    if proizv not in model:
      model = proizv + " " + model
    models_name.append(model + " ")
    #пробуем удалить 1 слово
    model1 = model.split(' ', 1)[1]
    if model1 not in no_words:
      if contains_only_digits_and_spaces(model1) != True:
        models_name.append(model1 + " ")
    #пробуем удалить 2 слово
    try:
      model2 = model1.split(' ', 1)[1]
      if contains_only_digits_and_spaces(model2) != True and model2 not in no_words:
        models_name.append(model2 + " ")
    except:
      pass
    prod_dict["Model"] = models_name

    #Пробуем получить цвет:
    colors = []
    color = row[8].strip().lower()
    colors.append(color)
    color_eng =  GoogleTranslator(source='ru', target='en').translate(color)
    colors.append(color_eng.lower())
    if color == "золотой":
      colors.append("starlight")
    if color == "фиолетовый":
      colors.append("purple")
    if color == "серый космос":
      colors.append("grey")
      colors.append("gray")
    if color == "серый":
      colors.append("gray")
    prod_dict["Color"] = colors

    #Пробуем получить оперативную память
    op_stor = ""
    try:
      op_stor = row[4].strip().lower()
    except:
      try:
        op_stor = re.search(r'(\d+)/', row[0].strip().lower()).group(1)
      except:
        pass
    if op_stor != "":
      prod_dict["OPStorage"] = [op_stor]
    #Пробуем получить память:
    name = row[0].strip().lower()
    if type(row[10]) is str:
      df_stor = row[10].strip().lower()
    else:
      df_stor=""
    stor = ""
    if df_stor=="":
      try:
        stor = re.search(r'(\d+)(?=\s*[GTТГ][BБ])', name, re.IGNORECASE).group(1)
      except:
        try:
          stor = re.search(r'/(\d+)\s', name).group(1)
        except:
          continue
    else:
      stor = re.search(r'(\d+)(?=\s*[GTТГ][BБ])', df_stor, re.IGNORECASE).group(1)
    if stor != "":
      stors = []
      if stor == "1":
        stors.append(stor + "tb")
        stors.append(stor + "тб")
        stors.append("1024")
        if op_stor != "":
          stors.append(op_stor + "+" + stor + "tb")
          stors.append(op_stor + "/" + stor + "tb")
          stors.append(op_stor + "+" + stor + "тб")
          stors.append(op_stor + "/" + stor + "тб")
          stors.append(op_stor + "+" + "1024")
          stors.append(op_stor + "/" + "1024")
      else:
        stors.append(stor)
        if op_stor != "":
          stors.append(op_stor + "+" + stor)
          stors.append(op_stor + "/" + stor)
      prod_dict["Storage"] = stors
    flag = False
    #Находим поставщиков:
    for index2, row2 in df_prices.iterrows():
      post_name = str(row2[0]).strip().lower()
      #Убираем пока цену в конце
      post_name = re.sub(r'\s*[-]?\s*[\d₽]+(?=[^\w\s]*$)', '', post_name).strip()
      has_mod = False
      has_col = False
      has_stor = False
      has_opstor = False
      for mod in prod_dict["Model"]:
        if mod in post_name:
          if check_keywords_in_strings(model, post_name):
            if mod[0].isdigit():
              if post_name[post_name.index(mod)-1] == "" or post_name[post_name.index(mod)-1] == " ":
                if "note" in post_name and "note" in model:
                  has_mod = True
                if "note" not in post_name and "note" not in model:
                  has_mod = True
            else:
              if "note" in post_name and "note" in model:
                has_mod = True
              if "note" not in post_name and "note" not in model:
                has_mod = True
      for col in prod_dict["Color"]:
        if col in post_name:
          has_col = True
      for st in prod_dict["Storage"]:
        if st in post_name:
          has_stor = True
      try:
        for opst in prod_dict["OPStorage"]:
          if opst in post_name:
            has_opstor = True
      except:
        has_opstor = True
      if has_mod and has_col and has_stor and has_opstor:
        pricee = ""
        matches =  re.findall(r'\d+', str(row2[0]).strip().lower())
        for match in reversed(matches):
          if len(match) > 3:
            pricee = match
            break
        add_row_itog(row[1], row[0].strip(), row2[1], pricee)
        add_row(index+1, row[3].strip().lower(), index2+2, post_name, str(prod_dict))
        flag = True
    if flag != True: pass


df_res_itog.to_csv('итоговая таблица.csv', index=False, sep=',', encoding='utf-8-sig')
df_res.to_csv('сопоставленные данные.csv', index=False, sep=',', encoding='utf-8-sig')