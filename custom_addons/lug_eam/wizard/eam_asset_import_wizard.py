# -*- coding: utf-8 -*-

from odoo import models


class EamAssetImportWizard(models.TransientModel):
    _name = "eam.asset.import.wizard"
    _description = "Import tài sản từ CSV"

    # MVP: dùng import chuẩn Odoo + file mẫu trong ST_Asset_Management/templates/
    # Wizard giữ chỗ cho map phức tạp ở pha sau.
