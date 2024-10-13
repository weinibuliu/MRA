from pathlib import Path
import csv
import json

from maa.toolkit import Toolkit
from maa.context import Context
from maa.custom_action import CustomAction
from maa.custom_recognition import CustomRecognition

main_path = Path.cwd()

def main():
    # 注册自定义动作
    Toolkit.pi_register_custom_action("GetGoodsData",GetGoodsData())
    # 启动 MaaPiCli
    Toolkit.pi_run_cli(f"{main_path}/assets", f"{main_path}/cache", False)

class GetGoodsData(CustomAction):
    def run(self, context: Context, argv: CustomAction.RunArg) -> bool:
        cache = json.loads(argv.custom_action_param)
        city_name = cache["city_name"]
        goods_name = cache["goods_name"]

        getroi_pipe={"Getroi":{"timeout": 3000,
                                "recognition": "TemplateMatch",
                                "template": f"goods/{city_name}/{goods_name}.png",
                                "roi": [500,140,135,545]
                                }}

        context.override_pipeline(getroi_pipe)
        context.run_pipeline(entry="Getroi")

        ocr_pipe = {"OCRTask":{"recognition": "OCR",
                               "roi": "Getroi",
                               "roi_offset": [205,15,35,-30],
                               "expected":"^[1-9].*%$"}}

        # OCR ON
        reco_detail = None
        reco_detail = context.run_recognition("OCRTask", context.tasker.controller.post_screencap().wait().get(), pipeline_override=ocr_pipe)
        if reco_detail is not None:
            print(f"{goods_name}：{reco_detail.best_result.text}")
        else:
            print(f"{goods_name}:None")

        return True

if __name__ == "__main__":
    main()