import sys; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit
e=wledit.Editor('files/orig2020.rvt')
# descending offsets: room (2900614) < symbol (3257483) -> do symbol first
print(e.set_string(1040365,'SymbolInfo.m_name','200UB25.4-RENAMED-TYPE'))
print(e.set_string(857191,'ParamValueAString.m_value','Master Bedroom Renamed Longer',match='Master Bedroom'))
e.save('files/e4_2020.rvt')
