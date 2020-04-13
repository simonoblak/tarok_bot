from Logs import Logs


class RoundCards:
    def __init__(self, round_id, card_ids, talon_ids, put_down_ids, stack):
        self.round_id = round_id
        self.card_ids = card_ids
        self.talon_ids = talon_ids
        self.put_down_ids = put_down_ids
        self.stack = stack

    def get_values(self):
        if len(self.talon_ids) == 0 and len(self.put_down_ids) == 0:
            return [(self.round_id, c_id, 0, 0, self.stack) for c_id in self.card_ids]
        values = []
        card_and_talon_ids = []
        if self.stack != "stack0" and self.stack != "tarot":
            card_and_talon_ids = [v for v in self.card_ids if v not in self.talon_ids] + self.put_down_ids
        else:
            card_and_talon_ids = self.card_ids + self.talon_ids

        for c_id in card_and_talon_ids:
            t_id = 1 if c_id in self.talon_ids else 0
            p_id = 1 if c_id in self.put_down_ids else 0
            values.append((self.round_id, c_id, t_id, p_id, self.stack))
        Logs.debug_message("RoundCards.get_values(): Printing values of RoundCards")
        Logs.debug_message(values)
        return values
