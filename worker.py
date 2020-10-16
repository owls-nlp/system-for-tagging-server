from tagging_system import Document, SegmentationModel, FindingFormulasModel
import sqlite3
import time


def process_document(pdf_path, segmentation_model, finding_formulas_model, layout_type, langs, original_filename, document_type):
    doc = Document(
        pdf_path = pdf_path, 
        segmentation_model = segmentation_model,
        finding_formulas_model = finding_formulas_model, 
        layout_type = layout_type,
        document_type = document_type,
        langs = langs,
        dpi = 900,
        tessdata_dir = '/usr/share/tesseract-ocr/4.00/tessdata'
    )

    file_name = original_filename.split('.')[0]

    return doc.convert(output_type='docx', output_filename=f'{file_name}.docx', to_zip = True)


def update_zip_path(zip_path, id_doc):
    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    sql = f"UPDATE files_info SET zip_path = '{zip_path}' WHERE id = '{id_doc}'"
    
    cursor.execute(sql)
    conn.commit()
    conn.close()


seg_model = SegmentationModel(
    path_to_model = './models/MaskRCNN_Resnext101_32x8d_FPN_3X.pth',
    path_to_cfg_config = './configs/DLA_mask_rcnn_X_101_32x8d_FPN_3x.yaml',
    device = 'cpu',
    score_thresh_test = 0.5
)


find_model = FindingFormulasModel(
    path_to_model =  './models/AMATH512_e1GTDB.pth',
    score_thresh_test = 0.3
)


while True:
    conn = sqlite3.connect("tagging_system.db")
    cursor = conn.cursor()

    sql = f"SELECT * FROM files_info WHERE pdf_path is not NULL and zip_path is NULL and column_type is not NULL and document_type is not NULL"
    cursor.execute(sql)
    result = cursor.fetchall()
    
    if len(result) > 0:
        for doc in result:
            id_doc = doc[0]
            pdf_path = doc[1]
            layout_type = doc[4]
            langs = doc[5].split('+')
            original_filename = doc[6]
            document_type = doc[7]
            zip_path = process_document(pdf_path, seg_model, find_model, layout_type, langs, original_filename, document_type)
            update_zip_path(zip_path, id_doc)

    time.sleep(10)

