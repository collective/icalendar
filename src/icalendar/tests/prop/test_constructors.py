
from icalendar.prop  import  vBoolean,vInline , vUTCOffset, vCategory, vCalAddress, vWeekday, vDuration, vFloat, vGeo, vInt,  vText, vMonth, vUTCOffset, vFrequency,  vRecur,  vDatetime, vDDDTypes, vUri
import datetime

def test_param_vCategory():
    try:
        obj = vCategory(["Work", "Personal"], params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vCategory)  
    except Exception as e:
        assert False, f"Error creating vCategory object: {e}"  

def test_param_vCalAddress():
    try:
        obj = vCalAddress('mailto:jane_doe@example.com',params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vCalAddress) 
    except Exception as e:
        assert False, f"Error creating vCalAddress object: {e}"  

def test_param_vWeekday():
    try:
        obj = vWeekday("2FR",params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vWeekday)  
    except Exception as e:
        assert False, f"Error creating vWeekday object: {e}"  

def test_param_vBoolean():
    try:
        obj = vBoolean(True, params={"SOME_PARAM":"VALUE"})  
        assert isinstance(obj, vBoolean)  
    except Exception as e:
        assert False, f"Error creating vBoolean object: {e}" 

def test_param_vDuration():
    try:
        td=datetime.timedelta(days=15, seconds=18020)
        obj = vDuration(td, params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vDuration)  
    except Exception as e:
        assert False, f"Error creating vDuration object: {e}"  

def test_param_vFloat():
    try:
        obj = vFloat('1.333',params={"SOME_PARAAM":"VALUE"})
        
        assert isinstance(obj, vFloat)  
    except Exception as e:
        assert False, f"Error creating vFloat object: {e}"  

def test_param_vGeo():
    try:
        obj = vGeo((37.386013, -122.082932),params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vGeo) 
    except Exception as e:
        assert False, f"Error creating vGeo object: {e}"  

def test_param_vInt():
    try:
        obj = vInt('87',params={"SOME_PARAAM":"VALUE"})  
        assert isinstance(obj, vInt)  
    except Exception as e:
        assert False, f"Error creating vInt object: {e}"  

def test_param_vInline():
    try:
        obj = vInline("sometxt", params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vInline)  
    except Exception as e:
        assert False, f"Error creating vInline object: {e}"  
def test_param_vText():
    try:
        obj = vText("sometxt", params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vText)  
    except Exception as e:
        assert False, f"Error creating vText object: {e}"  

def test_param_vMonth():
    try:
        obj = vMonth(1,params={"SOME_PARAAM":"VALUE"})  
        assert isinstance(obj, vMonth)  
    except Exception as e:
        assert False, f"Error creating vMonth object: {e}"  

def test_param_vUTCOffset():
    try:
        obj =  vUTCOffset(datetime.timedelta(days=-1, seconds=68400),params={"SOME_PARAM":"VALUE"})  
        assert isinstance(obj, vUTCOffset)  
    except Exception as e:
        assert False, f"Error creating vUTCOffset object: {e}"  

def test_param_vFrequency():
    try:
        obj = vFrequency("DAILY",params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vFrequency) 
    except Exception as e:
        assert False, f"Error creating vFrequency object: {e}"  

 
def test_param_vRecur():
    try:
        obj =vRecur({'FREQ': ['DAILY'], 'COUNT': [10]}, params={"SOME_PARAAM":"VALUE"})
    except Exception as e:
        assert False, f"Error creating vRecur object: {e}"  

def test_param_vDatetime():
    try:
        dt = datetime.datetime(2025, 3, 16, 14, 30, 0, tzinfo=datetime.timezone.utc)
        obj = vDatetime(dt,params={"SOME_PARAAM":"VALUE"})  
        assert isinstance(obj, vDatetime)  
    except Exception as e:
        assert False, f"Error creating vDatetime object: {e}"  
def test_param_vUri():
    try:
        obj = uri_instance = vUri("WWW.WESBITE.COM",params={"SOME_PARAAM":"VALUE"}) 
        assert isinstance(obj, vUri)  
    except Exception as e:
        assert False, f"Error creating vUri object: {e}"  