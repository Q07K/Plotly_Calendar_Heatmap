## 일별 빈도 시각화 Calendar Heatmap
`Pandas`와  `Plotly`를 사용하여 간편한 Calendar Heatmap 제작을 지원합니다.

__1, Install__
```python
pip install -U git+https://github.com/Q07K/Plotly_Calendar_Heatmap
```

__2.  사용방법__
- import 및 초기 설정(date column은 datetime64로 자동 변환됩니다. )
```python
import pandas as pd
from CalendarHeatmap import CalendarHeatmap

# Load data
df = pd.read_csv('./data/test_user1_data.csv')
print(df['date'].dtype)

# used
calendar = CalendarHeatmap(
	df,
	date_col='date',
	value_col='chat',
	language=True  # True: Kor
)
print(calendar.data['date'].dtype)
```
<br>
```
object
datetime64[ns]
```

-  시각화 가능한 년도 확인 및 Calendar Heatmap 출력
```python
# 시각화 가능한 년도 확인
print(calendar.years)
```

```
[2022 2023]
```

```python
# correct
calendar.make_trace(year=2022)
```
![[newplot (22).png]]

```python
#wrong
calendar.make_trace(year=2024)
```

```
ValueError: "2024" not in list: [2022 2023]
```

- event 적용
```python
# event setting
event_df = df.loc[df.event.notna(), ['date', 'event']]
display(event_df)

```
![[Pasted image 20231102153609.png]]

```python
calendar.on_event(event_df, date_col='date', event_col='event')
calendar.make_trace(year=2022)
```

![[newplot (23).png]]


## 목차
- [개요](#개요)
- [설명](#설명)
- [버전](#버전)


## 개요
- 프로젝트 이름: Calendar Heatmap
- 멤버: 김규형
- 프로젝트 기간: 2023.10 ~ 2023.10
- 개발 언어: Python
- 패키지: Pandas, Plotly
- 개발 환경
	- Python 3.8.13
	- Pandas 2.0.3
	- Numpy 1.24.4
	- Plotly 


## 설명
> __문제정의__
> 사용자의 일별 활동 빈도를 `Calendar Heatmap`으로 표현 하기 위해 진행된 Sub Project로써,
> `Dash` 활용의 확장성을 위해 `Plotly`를 사용하였으며,  Seaborn과 같은 사용 편의성을 제공하기 위해 `Pandas`를 사용하였다.


## 버전
- 1.0.0-alpha `2023-10-27` ~ `2023-11-02`
	- 개별적 기능 구현
	- 패키징
- 1.0.0-beta `2023-11-02`
- 1.0.1-beta `2023-11-02`
	- Modify instance variables

- 1.0.0-release `20yy-mm-dd`

