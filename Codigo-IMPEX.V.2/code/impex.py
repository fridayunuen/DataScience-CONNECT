import Directory as Dir
import V_Imagenes as vi
import os
import pandas as pd
import V_I_Cubo as ivc

tallas = ivc.tallas
# substract first 7 characters from each value in tallas
sku = [x[:10] for x in tallas]

tallas = pd.DataFrame({"tallas": tallas, "sku": sku})

def get_tallas(tallas,sku):
    tallas = tallas[tallas['sku'] == sku]
    tallas = tallas['tallas'].values
    return tallas

init = ["$productCatalog=shasaProductCatalog",
"$productCatalogName=shasaProductCatalog",
"$catalogVersion=catalogversion(catalog(id[default=$productCatalog]),version[default='Online'])[unique=true,default=$productCatalog:Online]",
"$media=@media[translator=de.hybris.platform.impex.jalo.media.MediaDataTranslator]",
"$medias=medias(code, $catalogVersion)",
"$picture=picture(code, $catalogVersion)",
"$galleryImages=galleryImages(qualifier, $catalogVersion)",
"$thumbnail=thumbnail(code, $catalogVersion)",
"$thumbnails=thumbnails(code, $catalogVersion)",
"$detail=detail(code, $catalogVersion)",
"$normal=normal(code, $catalogVersion)",
"$others=others(code, $catalogVersion)",
"$data_sheet=data_sheet(code, $catalogVersion)",
"$individualPhotos=individualPhotos(code, $catalogVersion)"
]

head = ["INSERT_UPDATE Media;code[unique=true];$media;mime[default='image/jpg'];folder(qualifier);mediaFormat(qualifier);$catalogVersion"]
head_product= ["INSERT_UPDATE Product;code[unique=true];$picture;$thumbnail;$detail;$others;$normal;$thumbnails;$galleryImages;$catalogVersion"]


vi.Mapping['sku'] = vi.Mapping['sku'].astype(str)


for lote in vi.Mapping["Lote"].unique():

    Mapping = vi.Mapping[vi.Mapping["Lote"] == lote]
    dir = "Lote"+str(lote)
    os.chdir(Dir.resultados_hoy + r"\\" + dir)
    file = open("impex1.impex", "w")
    
    file.write("\n".join(init))
    file.write("\n")
    file.close()

    file2 = open("impex2.impex", "w")

    file2.write("\n".join(init))
    file2.write("\n")
    file2.close()

    for sku in Mapping['sku'].unique():
        
        df = Mapping[Mapping['sku'] == sku]
        
        tallas_sku = get_tallas(tallas,str(sku))

        sufijo = df["suffix"].unique()
        file = open("impex1.impex", "a")
        file.write("\n".join(head))
        file2 = open("impex2.impex", "a")
        file.write("\n")

        for suf in sufijo:
            df1 = df[df['suffix'] == suf].reset_index(drop=True)
            for index in range(len(df1)):
                size = df1.loc[index, 'W'] + "Wx" + df1.loc[index, 'H'] + "H"
                asignacion = ";/"+ str(df1['suffix'][index])+"/" +size +"/"+str(df1['sku'][index]) +";"+ str(df1['filename'][index]) +";images;images;"+ size+";"
                asignacion = asignacion.replace(";300Wx300H_",";400Wx600H_")

                file.write(asignacion)
                file.write("\n")
            ####    
            file.write(";/"+ str(df1['suffix'][index])+"/30Wx30H/"+str(df1['sku'][index]) +";65Wx65H_"+str(df1['sku'][index])+"_"+str(suf)+".jpg"+";images;images;30Wx30H;")    
            file.write("\n")

        file.write("INSERT_UPDATE MediaContainer;qualifier[unique=true];$medias;$catalogVersion")   
        file.write("\n")


        file2.write("\n".join(head_product))
        file2.write("\n")

        content = []
        for sufi in sufijo:
            df1 = df[df['suffix'] == sufi].reset_index(drop=True)

            #values = "/"+df1["W"]+ "Wx" + df1["H"] + "H"+"/"+ df1["sku"]
            values = "/"+str(sufi)+"/"+df1["W"]+ "Wx" + df1["H"] + "H"+"/"+ df1["sku"]
            values = values.str.cat(sep=",")

            cont = str(sku)+str(sufi)
            content2 = []
            for s in sufijo:
                content2.append(str(sku) + str(s)) 
    
            content.append(cont)

            #file.write(";"+cont+";"+values)
            file.write(";"+cont+";"+values+",/"+ str(sufi)+ "/30Wx30H/"+sku)
            file.write("\n")

            # Ranuras
            #medidas = ["1200Wx1200H","96Wx96H","515Wx515H","65Wx65H"]
            medidas = ["1200Wx1200H","96Wx96H","300Wx300H","515Wx515H","65Wx65H"]
            suf ="/"+str(sufi)+"/"
            medidas = [suf + x for x in medidas]
            medidas = ("/"+str(sku)+";").join(medidas)+"/"+str(sku)+";/"+str(sufi)+"/30Wx30H/"+str(sku)+";"

            ranura = medidas+",".join(content2)+";"

            file2.write(";"+str(sku)[0:7]+"_"+str(sku)[7:10]+";"+ranura)
            file2.write("\n")

            for talla in tallas_sku:                 
                row =";" +talla[0:7]+"_"+talla[7:len(talla)]+";" + ranura 
                file2.write(row)
                file2.write("\n")
            
        file.close() 
        file2.close() 
        


Mapping = vi.Mapping
       
print("Archivos impex creado con exito")        