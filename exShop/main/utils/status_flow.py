# utils/status_flow.py

from main.models import StatusTransition

class StatusFlowManager:
    """
    販売状況（Status）の状態遷移を制御・取得するユーティリティクラス。
    遷移元ステータスに応じた遷移先ステータスの検索などを行う。

    使用例:
        flow = StatusFlowManager(current_status)
        next_status = flow.get_next()
    """

    def __init__(self, current_status):
        """
        コンストラクタ。遷移元の販売状況を初期化。

        引数:
            current_status (Status): 現在の販売状況オブジェクト
        """
        self.current_status = current_status

    def get_next(self):
        """
        現在の販売状況に対応する遷移先を取得。

        戻り値:
            Status または None: 次に遷移可能なステータスが存在する場合はそのオブジェクト、なければ None。
        """
        # StatusTransition モデルから、現在のステータスに対応する遷移を検索
        transition = StatusTransition.objects.filter(from_status=self.current_status).first()

        # 遷移が見つかればその遷移先を返却。見つからなければ None を返す。
        return transition.to_status if transition else None
