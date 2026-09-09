from tekb_core.research_batch_config_v1_locked import canonical_payload, lock_metadata
from tekb_core.canonical_serializer import compute_configuration_hash

def generate_candidates():
    sl_grid = canonical_payload["grid"]["sl_grid_atr"]
    tp_grid = canonical_payload["grid"]["tp_grid_atr"]
    hold_grid = canonical_payload["grid"]["max_hold_bars"]
    actual_count = len(sl_grid) * len(tp_grid) * len(hold_grid)
    expected = canonical_payload["multiple_testing"]["expected_count_assertion"]
    print(f"SL={len(sl_grid)} TP={len(tp_grid)} HOLD={len(hold_grid)} TOTAL={actual_count} Expected={expected}")
    if actual_count != expected:
        print("FAIL count tidak sama")
        return []
    candidates = []
    for sl in sl_grid:
        for tp in tp_grid:
            for h in hold_grid:
                candidates.append(f"CAND_{sl}ATR_{tp}ATR_{h}")
    return candidates

if __name__ == "__main__":
    grid = generate_candidates()
    print(f"Berhasil buat {len(grid)} kandidat")
    for c in grid[:5]:
        print(c)
    print("...")