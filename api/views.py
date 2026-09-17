from rest_framework.views import APIView
from rest_framework.utils.serializer_helpers import ReturnDict

from django.http import HttpResponse
from dotenv import load_dotenv
from io import BytesIO as IO
import xlsxwriter


load_dotenv()


class ExportView(APIView):
    def process_data(self, data):
        columns = [key for key in data[0].keys() if key != "id"]

        for col in columns:
            if all(isinstance(row[col], ReturnDict) for row in data):
                for row in data:
                    row[col] = row[col].get("name")

        excel_file = IO()
        workbook = xlsxwriter.Workbook(excel_file, {"in_memory": True})
        worksheet = workbook.add_worksheet("sheetname")

        for col_idx, col in enumerate(columns):
            worksheet.write(0, col_idx, col)
        for row_idx, row in enumerate(data, start=1):
            for col_idx, col in enumerate(columns):
                worksheet.write(row_idx, col_idx, row[col])

        workbook.close()
        excel_file.seek(0)
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # set the file name in the Content-Disposition header
        response['Content-Disposition'] = 'attachment; filename=myfile.xlsx'

        return response