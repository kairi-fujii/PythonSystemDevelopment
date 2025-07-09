# utils/transaction.py

from main.models import TransactionStatusTransition

def get_ordered_transaction_statuses():
    """
    TransactionStatus を進行順で返す。
    """
    # 全遷移マスタを取得
    transitions = TransactionStatusTransition.objects.all()
    forward_map = {
        t.from_status_id: t.to_status
        for t in transitions if t.from_status_id is not None
    }

    # 初期状態（from_status が None）
    start_transition = transitions.filter(from_status__isnull=True).first()
    if not start_transition:
        return []

    ordered = [start_transition.to_status]
    current = start_transition.to_status

    # forward_map をたどって順番に並べる
    while current.id in forward_map:
        next_status = forward_map[current.id]
        ordered.append(next_status)
        current = next_status

    return ordered
