from rest_framework.views import APIView
import rest_framework

from django.http import HttpResponse
from dotenv import load_dotenv
from io import BytesIO as IO
import pandas as pd


load_dotenv()


def column_is_type(col, t):
    return col.apply(type).eq(t).all()


class ExportView(APIView):
    def process_data(self, data):
        df = pd.DataFrame(data)
        df = df.drop(columns=["id"])
        for col in df.columns:
            if column_is_type(df[col], rest_framework.utils.serializer_helpers.ReturnDict):
                df[col] = df[col].apply(lambda x: x.get("name"))
        print(df)
        excel_file = IO()
        xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df.to_excel(excel_writer=xlwriter, sheet_name='sheetname',index=False)
        xlwriter.close()
        excel_file.seek(0)
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # set the file name in the Content-Disposition header
        response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'

        return response