from tickets import add_faculty, connect, faculties, latest, search, sell

con = connect(":memory:")
add_faculty(con, "ETF")
add_faculty(con, " ETF ")
assert faculties(con) == ["ETF"]
assert sell(con, "0123/2024", "ETF", 1) is None
assert sell(con, "0123/2024", "ETF", 1)          # duplicate same day
assert sell(con, "0123/2024", "ETF", 2) is None  # other day ok
for bad in ["123/2024", "0123-2024", "0123/24", "abcd/2024", "0123/20245"]:
    assert sell(con, bad, "ETF", 1), bad

for i in range(7):
    assert sell(con, f"{i:04}/2023", "ETF", 3) is None
assert [r[0] for r in latest(con)] == ["0006/2023", "0005/2023", "0004/2023", "0003/2023", "0002/2023"]
assert search(con, "0123") == [("0123/2024", "ETF", 1), ("0123/2024", "ETF", 2)]
assert len(search(con, "etf")) == 9  # faculty match, case-insensitive
print("ok")
