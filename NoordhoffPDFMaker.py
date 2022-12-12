import os
import requests
from PIL import Image
import shutil
import tkinter as tk
from bs4 import BeautifulSoup as BS
import re

# Code for downloading and compressing
def Program (base_url, pages):
  # Make temporary directory
  os.mkdir("./ImageToPDF")

  # Download all pages as .jpg
  for page in range(pages):

    image_url = base_url + str(page+1) + ".jpg"

    img_data = requests.get(image_url).content
    with open("./ImageToPDF/"+ str(page+1) + ".jpg", 'wb') as handler:
      handler.write(img_data)

    page += 1

  filenames = []

  # Get all files in temporary directory
  for path in os.listdir("./ImageToPDF/"):
    if os.path.join(path,"./ImageToPDF/"):
      filenames.append(path)

  # Sort the files
  filenames.sort(key=lambda f: int(re.sub('\D', '', f)))

  # Open all images
  imageList = [
    Image.open("./ImageToPDF/" + image)
    for image in filenames
  ]

  # Make pdf of all images
  imageList[0].save(
    "./result.pdf", "PDF", resolution=150.0, save_all=True, append_images=imageList[1:]
  )

  # Remove temporary directory (with images)
  shutil.rmtree("./ImageToPDF")


#Extracting base url
def extract(input_url):
  # Split URL at /
  url_list = input_url.split("/")
  base_url = ""

  # Convert to https
  if url_list[0] == "http:":
    url_list[0] = "https:"

  elif url_list[0] != "https:":
    url_list.insert(0, "https:")
    url_list.insert(1, "")

  # Remove "jpg"
  if "jpg" in url_list[-1]:
    url_list.pop()

  elif url_list[-1] == "":
    url_list.pop()

  # Construct base URL
  match url_list[-1]:
    case "layout":
      url_list.append("")

    case "img":
      url_list.append("layout")
      url_list.append("")

    case "assets":
      url_list.append("img")
      url_list.append("layout")
      url_list.append("")

    case "extract":
      url_list.append("assets")
      url_list.append("img")
      url_list.append("layout")
      url_list.append("")

    case other:
      url_list.append("extract")
      url_list.append("assets")
      url_list.append("img")
      url_list.append("layout")
      url_list.append("")

  # Add all / back
  for i in range(len(url_list) - 1):
    base_url += url_list[i] + "/"
    i += 1

  return base_url


# Converging to page number (guess and check algorithm)
def converge(base_url, lower, upper):
  middle = ((upper - lower) // 2) + lower

  image_url1 = base_url + str(middle) + ".jpg"
  image_url2 = base_url + str(middle+1) + ".jpg"
  soup1 = BS(requests.get(image_url1).content, "html.parser")
  soup2 = BS(requests.get(image_url2).content, "html.parser")

  if "blob" not in str(soup1) and "blob" in str(soup2) :
    return base_url, middle

  if "blob" not in str(soup1) and "blob" not in str(soup2) :
    return converge(base_url, middle, upper)

  return converge(base_url, lower, middle)



# Code for UI
root = tk.Tk()
canvas = tk.Canvas(root, width=300, height=300)
root.title("Noordhoff PDF Maker")
root.geometry("600x200")

def clicked():
  # Destoying all widgets except original ones
  for widget in root.winfo_children():
    if str(widget) == ".!canvas" or str(widget) == ".!label" or str(widget) == ".!entry" or str(widget) == ".!button":
      continue

    else:
      widget.destroy()

  root.update()

  if e_url.get() == "":
    l_errval = tk.Label(root, text="Please enter a value", fg="black", font=("consolas", 12, "bold"), anchor="w")
    l_errval.pack(fill="both")
    l_errval.place(height=20, width=500, x=0, y=75)

  else:
    try:
      l_calc = tk.Label(root, text="Program is now calculating...", fg="black", font=("consolas", 12, "bold"), anchor="w")
      l_calc.pack(fill="both")
      l_calc.place(height=20, width=500, x=0, y=75)
      root.update()

      base_url, pages = converge(extract(e_url.get()), 1, 2000)

      l_appr = tk.Label(root, text="Program will take approximately " + str(round(pages*0.055)+1) + " seconds to run", fg="black", font=("consolas", 12, "bold"), anchor="w")
      l_appr.pack(fill="both")
      l_appr.place(height=20, width=500, x=0, y=75)

      b_cont = tk.Button(text="Click to continue running", command= lambda: continued(base_url, pages), bg="white", fg="black")
      b_cont.pack()
      b_cont.place(height=20, width=200, x=0, y=100)
      root.update()

    except:
      print("except")
      try:
        base_url, pages = converge(extract(e_url.get()), 1, 2010)

        l_appr = tk.Label(root, text="Program will take approximately " + str(round(pages*0.055)+1) + " seconds to run", fg="black", font=("consolas", 12, "bold"), anchor="w")
        l_appr.pack(fill="both")
        l_appr.place(height=20, width=500, x=0, y=75)

        b_cont = tk.Button(text="Click to continue running", command= lambda: continued(base_url, pages), bg="white", fg="black")
        b_cont.pack()
        b_cont.place(height=20, width=200, x=0, y=100)
        root.update()

      except:
        l_errurl = tk.Label(root, text="Please enter a valid URL", fg="black", font=("consolas", 12, "bold"), anchor="w")
        l_errurl.pack(fill="both")
        l_errurl.place(height=20, width=500, x=0, y=75)


def continued(base_url, pages):
  l_run = tk.Label(root, text="Program is now running...", fg="black", font=("consolas", 12, "bold"), anchor="w")
  l_run.pack(fill="both")
  l_run.place(height=20, width=500, x=0, y=125)
  root.update()

  Program(base_url, pages)

  l_done = tk.Label(root, text="Download and compression are done.\nResult is located in result.pdf", fg="black", font=("consolas", 12, "bold"), anchor="w", justify="left")
  l_done.pack(fill="both")
  l_done.place(height=40, width=500, x=0, y=125)


l_url = tk.Label(root, text="Input URL of image", fg="black", font=("consolas", 12, "bold"), anchor="w")
e_url = tk.Entry(root)
b_run = tk.Button(text="Click to run program", command=clicked, bg="white", fg="black")

l_url.pack(fill="both")
l_url.place(x=0, y=0)
e_url.pack()
e_url.place(height=20, width=500, x=0, y=25)
b_run.pack()
b_run.place(height=20, width=200, x=0, y=50)

root.mainloop()