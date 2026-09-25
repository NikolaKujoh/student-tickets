from tickets import add_faculty, connect, faculties, latest, remove_faculty, search, sell

con = connect(":memory:")
add_faculty(con, "ETF")
add_faculty(con, " ETF ")
assert faculties(con) == ["ETF"]
assert sell(con, "0123/2024", "ETF", 1) is None
assert sell(con, "0123/2024", "ETF", 1)          # duplicate same day
assert sell(con, "0123/2024", "ETF", 2) is None  # other day ok
assert sell(con, "", "ETF", 1)                  # empty index rejected
assert sell(con, "RN 12/23a", "ETF", 1) is None  # any other text is fine
assert sell(con, "RN 12/23a", "", 1)             # faculty required

for i in range(7):
    assert sell(con, f"{i:04}/2023", "ETF", 3) is None
assert [r[0] for r in latest(con)] == ["0006/2023", "0005/2023", "0004/2023", "0003/2023", "0002/2023"]
assert search(con, "0123") == [("0123/2024", "ETF", 1), ("0123/2024", "ETF", 2)]
assert len(search(con, "etf")) == 10  # faculty match, case-insensitive

remove_faculty(con, "ETF")
assert faculties(con) == []
assert len(search(con, "etf")) == 10  # sold tickets survive faculty removal
print("ok")
