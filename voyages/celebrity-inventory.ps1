$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("bgv", "c1", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AKA_A2", "A", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PRC-CEL-CRUISE-SEARCH-PRD", "3966217075~rv=47~id=8740b27e0099d98a5f675dda021ea487", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bgv", "a1", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("wuc", "CAN", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("lang", "en", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("wul", "en", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main__sn", "1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main_ses_id", "1788764277245%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("currencyCode", "CAD", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("office", "MIA", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("affinity", "`"075fefbffc64a58b`"", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_lso", "6E213E890A68D8DDC4D9469A040B40730E9FA63905B61A4C668B205D90118ADA~YAAQbSTDF50KIHegAQAA+8ioeggABnawbZ6uWIJAwwzD6T2erfj3u2lh+DpINjw/ep2vqmSeHVP5IdBfeaWASgrgXixUkuIYqPn1RWAwvhW+ph9YTXjz6O5s3FMN7VgLAIsqNQ1qzIn+wrpDd8UDy2F9F9Efq6R5lYhQtJNktavBJKtoYFFmJXuykf7eK284/y85+BJ1v2rt8W1x+DcEUYBgyNlDpSTdiPIF53bDEJCaWsAI8y2AOCih7bGRfshY2FZdmFybqZXi/IBloqkb1LtjZ+uFf0bZ2pqCDhsWTpzwR2Zq39Aw/5UunyKmugkxDvUZEF2qECiQMIMLihOQHYYaslfZ73amxMbEawz+WzgqnqjCCXwWA5QeZVQh+nWXSTLvSGXzNUEO/8/hzrW4tY2JBvW9vLdbh+UClM0PrcRIABwaVWOXKGn+WzcyxLyHKq8yhgPRKk1hP3mvJAJy0yv2EpZWc0b2szwyHg==~1788764277561", "/", ".www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("country", "CAN", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rwd_id", "cb1b18a0-1a22-4593-9c23-aea5dfa03a28", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("cruiseSearchColor", "blue", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rcgCohorts", "cs:blue|", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("currency", "CAD", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PRC-CEL-GA-PRD-V2", "3966217076~rv=4~id=4303c6c9c398b91d5501c4453cb8442b", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("BVBRANDID", "6df2e1a3-c8a2-49c2-b128-e74c33d33d37", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("BVBRANDSID", "b8431873-78ba-4436-80ae-48ebc7026d3c", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("FavoritesExperience", "redesign", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PRC-CELEBRITY-GRAPH-PRD", "3966217076~rv=72~id=66978ef6220ba822fc228c3ffb746c72", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_splunk_rum_user_anonymousId", "9747d169293f3f3fb663d309d61965ca", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("guest_status", "Browsing_Guest", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("Persist_Embarkation_Port", "undefined", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("Persist_Currency_Code", "CAD", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("Persist_Stateroom_Category", "undefined", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("Persist_BKPRODID_SAILDATE", "_", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("Persist_Sail_Date", "undefined", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("arsc_throttle", "arsc_demo", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main_vapi_domain", "celebritycruises.com", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_fbp", "fb.1.1788764278321.517284379874585559.Bg", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main_v_id", "01a07aa8ce3a0012b2be0fc74c260506f004e067019b8", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main_dc_visit", "1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "78967871E32B6490B32090C5BB7B59F4~000000000000000000000000000000~YAAQbSTDF7QOIHegAQAAIc6oegF4B2984w9J+dUlv3iDVu13+u4bniIx12h1sZv8aRx4VfyQIA3blEVL65HxZUuDW5386+ZMjtXUkELCt7WCLZ+ul80xVGmoTHt5fuq7YUoouUKnZKM9fqu3z3ELoe+Rl7Gjrfg179PfCrnjNKT5cq7qyOTtP5BsdQ2lIwC3rPDduHUGPJAHlsHFbfRLA8waiCtzxixeJn0MWxLzLttqzxbDkN2lhSn5Z/YUFFu3VWuBMyu9hjAxn+pqLA3g/f1onXMtCHksWAy8WVJZjw5bUvkq+i+PzbWb8FESr+557C/KjzBWh3omydjvbLKXCetDyUt7UuLDVuZzg6ZNY7EaBauJNiQZYwixvjP7Mq3T01iAhlzc9KyS9dFBnWYTZH6DOgBXp/roDSGCc6z6dEkGwh/hEiV51QC7RIIi/fXzUS/iZR2eO3f7dEZ8tvFnMu2Z50556K2M", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCVS_981337045329610C0A490D44%40AdobeOrg", "1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main_dc_region", "us-east-1%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("at_check", "true", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_cs_mk_aa", "0.27350840102394147_1788764278744", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__td_signed", "true", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_scid", "Br-eEEItb09aVzT_oE2SlwDEWqjJA3Gm", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_dpm_ses.a7b8", "*", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__adal_ses", "*", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__adal_ca", "so%3Dchatgpt.com%26me%3D%28not%2520set%29%26ca%3D%28not%2520set%29%26co%3D%28not%2520set%29%26ke%3D%28not%2520set%29%26cg%3DUnknown", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__adal_cw", "1788764278862", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_tt_enable_cookie", "1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ttp", "01M1XAHM2VV67QYAFT5BB7KZPM_.tt.1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("MGX_P", "cccdf0ca-34d7-42ea-a56e-31a5d41111a3", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("MGX_PX", "36e0d85f-ab25-415b-8250-8e423a774459", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("MGX_CID", "1ea798bf-b083-4412-8b79-6e6632ae61f7", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ecid", "MCMID%7C64115130324317353941509023878506853517", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga", "GA1.1.726819333.1788764279", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCV_981337045329610C0A490D44%40AdobeOrg", "1585540135%7CMCIDTS%7C20704%7CMCMID%7C64115130324317353941509023878506853517%7CMCAAMLH-1789369078%7C7%7CMCAAMB-1789369078%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1788771478s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gpv_pn", "findacruise", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_cc", "true", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__qca", "P1-4d91bb7a-fb9f-4671-8272-fa389b2346a8", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("adcloud", "{%22_les_v%22:%22c%2Cy%2Ccelebritycruises.com%2C1788766079%22}", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_cs_c", "0", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("tfpsi", "f1558fbe-eff6-4408-ab54-e9bb664375af", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_pin_unauth", "dWlkPVl6UXhZVEEzT0dNdFltWmhOaTAwTVdFNUxXSXdOMlF0TW1Wa05qUTBaVGRpWWpjMA", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("cs-ab-version", "control", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_clck", "18wz6fh%5E2%5Eg99%5E0%5E2441", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main__ss", "0%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("PIM-SESSION-ID", "ZkbhfK9heLH18R4d", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("OptanonConsent", "isGpcEnabled=0&datestamp=Mon+Sep+07+2026+02%3A58%3A00+GMT-0400+(Eastern+Daylight+Time)&version=202411.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=833786ea-5225-47fa-96c8-1bd76bddf6fc&interactionCount=1&isAnonUser=1&landingPath=https%3A%2F%2Fwww.celebritycruises.com%2Fca%2Fcruises%3Fcountry%3DCAN%26utm_source%3Dchatgpt.com&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0007%3A1%2CC0004%3A1", "/", ".www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main__prevpage", "findacruise%3Bexp-1788767880433", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main_dc_event", "2%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_td", "83d2d56a-4b50-4054-ae7d-63e8b9caa984", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__adal_id", "40ab2224-5900-4791-9f85-488188fd8f61.1788764279.2.1788764281.1788764279.52041763-f1a1-48d1-bec0-4adf68ac86a3", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_scid_r", "Hz-eEEItb09aVzT_oE2SlwDEWqjJA3GmazWv1g", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__rtbh.uid", "%7B%22eventType%22%3A%22uid%22%2C%22id%22%3A%22cb1b18a0-1a22-4593-9c23-aea5dfa03a28%22%2C%22expiryDate%22%3A%222027-09-07T06%3A58%3A00.596Z%22%7D", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__rtbh.lid", "%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22Z1piWeRSTfJQiFMl59LK%22%2C%22expiryDate%22%3A%222027-09-07T06%3A58%3A00.597Z%22%7D", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_dpm_id.a7b8", "81b4fd84-dda7-4e19-874f-c1a93dc8e8eb.1788764279.1.1788764281.1788764279.293443ac-93a0-431b-b86b-01efaa5b999d", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("mbox", "session#2124f28f05694e0d9c96f1d87c36d860#1788766141|PC#2124f28f05694e0d9c96f1d87c36d860.34_0#1852009081", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_getNewRepeat", "1788764280703-New", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppvl", "findacruise%2C18%2C18%2C1113%2C1953%2C1113%2C5120%2C1440%2C1.5%2CP", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_gcl_au", "1.1.156914101.1788764279.-.-.1788764278.1566825648.1788764279.1788764280", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetsid", "75cfa930aa8911f182467f8ec78bf74b|1icm5l6|2|g99|0|2441", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_cs_id", "77a13e3e-123c-ab27-981b-988f76f95670.1788764279.1.1788764280.1788764279.1756498085.1822928279049.1.x", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_cs_s", "2.5.U.9.1788766080875", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_cs_s_ctx", "%7B%22firstViewTime%22%3A1788764279050%2C%22firstViewUrl%22%3A%22https%3A%2F%2Fwww.celebritycruises.com%2Fca%2Fcruises%3Fcountry%3DCAN%26utm_source%3Dchatgpt.com%22%2C%22sessionReferrer%22%3A%22%22%7D", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kampyle_userid", "eae5-2035-669f-1558-7b22-67e5-baaf-75f6", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_sctr", "1%7C1788753600000", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid", "1788764278879::PAIOg-qA1yT7FPY2wKW5.1.1788764281322.0::1.391.2102::0.0.0.0::0.0.0", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid_CBHEBOJC77U5CF099TGG", "1788764278879::AhgYnjiHtVdTkHO1MBr8.1.1788764281322.1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kampyleUserSession", "1788764281332", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kampyleUserSessionsCount", "1", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kampyleUserPercentile", "69.28269651133854", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kampyleSessionPageCounter", "1", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_clsk", "1nz4pv3%5E1788764281383%5E2%5E0%5Eb.clarity.ms%2Fcollect", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetvid", "75cfea80aa8911f1b86777bd0f714a49|1wiqyrc|1788764281453|2|1|bat.bing.com/p/conversions/c/t", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("LPVID", "NiODAwOWZkM2E5YjUyZWE2", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("LPSID-51532229", "EjpSKBC8SpOtjv09EY80YA", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("MGX_VS", "1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_splunk_rum_sid", "%7B%22expiresAt%22%3A1788765186779%2C%22id%22%3A%22b544658cd1ef9d82bdedfc16955d70f4%22%2C%22startTime%22%3A1788764276521%7D", "/", "www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppv", "findacruise%2C18%2C18%2C1113%2C1036%2C1113%2C5120%2C1440%2C1.5%2CL", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_s", "YAAQbSTDF3NKIHegAQAAqxipegZI1+XwgxO5BIrokef6LWjxQ18qGExwaHSll+JMDQN4Yg/RpbI9gsz1/LTVM42xmLFG9+a9mQfpDaq1N/ErrCQ5A4zWcfptLPPpPfRswvL79sDNO1AaGVeid/n5pNj3uRS0sMFbtbSCmqLDQD0V+JU9j2vU4cbMN9Wd0sCaK2wvl3sEkHnfZ4ExhflRXMf+2FBNKpQ2nRZq+51J9/ausm3ac7suRiMibesiacwXx/2uD8DORwv5fIQl/cbseYiIYXMkMNvNW22wDtx3/5lBuc0xvtc5CJ6Vvp0BLKN0fNCTYtOB7wuBp8eWD5vxJAF7fM+RXOh8bbOxIs96KyHkKRjfTUhD/OVuep5Q9SwnOWuG6B0MaI4G4EIrQEJ0sU2zjsbhoBfd/iDhZap6MPQUfDm6CLSwZyx2IyA8G11O4TcT/HYm7tG+qaIUk5eAEBQ/dCqq8fYXRVghFdKnPcY3S3tv9uRU/9yQThaBX2FauJ4EF5BUbyMVc/18MKpOJKGaVyS9JHCZ78UQe3YYPwKFNIOpyf//ncjcvkY1c4UD6BYPV2mdnC43AatKVrT+uRsSJ78JRT3lvkRzOapA7HcWAve6sQQN3Ik5fpTqZ83aEfKjO3VXCH6gf7SrRAPo8Vz7rbipiLg9QzarRigXj1bOZjhpAv3O6z83T+cZZfAfS2bj9XFqZ6SCoGNoKkAaeEqM7IGL+LSujcT/vyu/NJnXfjBFazwhQzWv5C6OK9EIfZQSJPRQzClGMvkdQzpDNXMigSWJuL5MBqJIw9MoTE3Y5pdblEsWwQqW2gmFfaXTE/BpJBW533b7P4037ShW0yz06flki8tDUeB78li28fj1psiGm+4OBL4rwBwYbMkbpu6z5GWmUob5Qi0iYirkPymLZ6BdBqlDj8+hJD9BAHS8NpP/GQAJw4LwHet2usbnuq0mN/CCh9EgZZiE3oheN0szjHjoWhwsoQYMn67ogkd7JR0eZoj57q7r/aw2jRyKHbaabjjVHI3Inn5zIwSwoEYp22qgPTPHIAIw5GelcBG5LKIkKWs+JGIiQ/Ecy2qg7rY4vf/JzeIIasTdq3c9vMArqvhWsoDI", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_so", "8635C23BE1823D3908C29AF284BEF1FC97416ABA2B55EFA39A0221A4C7BB8394~YAAQbSTDF3RKIHegAQAAqxipegg8U7RLzFTKhqsOxPWoSenqjQUxcXrqf6LzQobpHm+e3ks33mJoQSHPJ/7Uvaa8NnE0Ep2IGj+kz8WsH2xbDgXZtlbZF2nQPz1mN7v8Tqe38xNGSyxZHW5v59IlKsNkSl3oa8IjuFGApEgmHFcLbvmZgKPfOlw9+FXQaSeHCuQHP/vNR4q+AvEsIhkZEFKDIp8qdNQHW7VOOCgFD4+uTxRo8jd3EZ7XoEQlosjRNZUf+Fa3emOI+PYPhqXvNpMytgETDeKbd0kCGE8zqVo/FNniKiOvOPTPJbbnqjguwlynp0O+G06w40H/XU+rw93CmCX5xYty4dAEe+ka9LdLeq8iDRg8JHVno/35lq6WQt83LL6ej1VMF/pUw/s6FnOTjfqOfYBTlWhfVwrbY/HCmnd2fNt06LyEmrGIW86cRIb3qwZQPNx1oXAzhOpHrMi6Dqt59T3pzuAsDA==", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sz", "E4A2B445099DB93C8C246095BEC3F0D3~YAAQbSTDF3ZKIHegAQAAqxipegGrNd+Cf0ugGXPXrklu37aFZXi277CXubygB01a1ofU6fcfUwKq7JW4f5qjc14I67vGHARBfXInW1pWDtNuNlDeqFe36Xf/zjXytUoyP9i5jF7cmj2L0DlxGxT77POe31CpxAVvqzItM/N+BXrDcsZBx03mIoNPTCTDibh/9YVD04vL7un1yamEIfRjaVIKZBxhUXSCWGGc2Czs1wvvE6fty6EZclrSt3Tw2ewVSZFissFkmJy5ODFDiFX+f43yB6RE4f0Avb5epG27gyi5zESlKGx6Rtd7kvDCIlV7NJdoH7Cmg05eZSV+gDEkoolff2T7Vvph7qydmWRUqWrM56ldWOrB8qZy437EH3ZRwKBFd1SGxXTR7s2bycZBdsSJ4RbBRBnZzOw2wxnkCiYkjEZGEJfWb5o=~3748151~4602181", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_LW3W0ELL5B", "GS2.1.s1788764278`$o1`$g1`$t1788764297`$j41`$l0`$h0`$ddKjCSRD0QUBFJi_mzieNe1a58Ji55I0pAg", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("RT", "`"dm=www.celebritycruises.com&si=361zwsoxds8&ss=1788764279270&sl=1&tt=794&obo=0&sh=1788764280065%3D1%3A0%3A794&rl=1`"", "/", ".www.celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main__se", "3%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main__st", "1788766097835%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("utag_main__pn", "3%3Bexp-session", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_abck", "66C721151F8320D5A2B0DCDB5813DB50~0~YAAQbSTDF9hLIHegAQAAdRqpehDrZIyAUb6QCH+XiF5r8rgy9KObukACdl+MbcclWgg0IOA3bhJf2wkwd8KKtcGEg/Nes4aszS/UscSnWtkQr0gp+EDZ36S6SQ26knvLUFi4w0Ecg3KwYXcUdNLovWK5QbmYrvkzIfPrV1j+esQOKhq6jBirnkErd3fm72QpKMZs483s8JD0OnMwzL/k3OiJ3kT3fmEoN69IqFJkh+S7IEWs6Oin7eL1rNQynTny9iXlpR15aZ3SO7sqZ31HYmh/IpnDtHtVAS3TMclYOXhjzo/XaLYfVSs+Py8/bJFACotEaih3uZIETaWda6Zt8ic16b9LSPYSmFR0AxYDvdgH1xxSfFZcvpeyE9xLZe9nWGeTimda8KvwQlTv7aQhsE23HIUkWmginHz8QNpI1bE+04cbdoJBGDV2kjSp5n5Ohsv4rAFZBqYyqkjtLCfjo1qCTlry13Vttnu129PPtmxL9qxfmAm9CH2Fd/Nr+RVagwzMVfJ1PE04jkRGj53ckjCwsttfV7wtc7yGZfKCuyUKR/COsNP1YY5UfOmPD5kIuwQstPdSfeAghlH5kYKBcDqMUPe3xE+WWZ/gxyXyMREF9zriX/3c5oaGWmieEdafbvcXCq2+aK3aO/zy5K9QIwOe4ygtAkZxHXk=~-1~-1~1788767877~AAQAAAAG%2f%2f%2f%2f%2f8I78FiBeGDQ%2fKgngk05X3RkY2tXkAkCBFJiuQfhfgXwbvk+xKAJNguhm5gIapivv6Ggj0XvJp9st4%2fKeNWgBMABf8T6rDGFQcxI~-1", "/", ".celebritycruises.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sv", "A1B5D05291CA5B74774BBF543B8949BB~YAAQbSTDF0FMIHegAQAA+BqpegE3VMOY7bdq3KJJqGHPZBpDECZQFqcK6s7Dnz4hXIxUhin4D5h97zbEb7T/gyYVvNCQAmfJVwamIL7t8M+SzrRR53T1bebC9P+Hd29Ps++ZdYN1j5DL8uS+z7K+hxQN6gG1I7nKv2njyNHpkbdsQ/dAElFGtucm6JZfp018aSQEQnLGMhtJFDm/rYqkWuy7BAJlzllwcLqvX/SRN4Yc+XsP9YeX8JvUeLv98jgpdqAVIqTr4gjF+MM=~1", "/", ".celebritycruises.com")))
$query = @'
query cruiseSearch_CruisesRiver($filters: String, $sort: CruiseSearchSort, $pagination: CruiseSearchPagination) {
  cruiseSearch(filters: $filters, sort: $sort, pagination: $pagination) {
    results {
      cruises {
        id
        productViewLink
        masterSailing {
          itinerary {
            name
            code
            voyageType
            days {
              number
              type
              ports {
                activity
                arrivalTime
                departureTime
                port {
                  code
                  name
                  region
                }
              }
            }
            departurePort {
              code
              name
              region
            }
            destination {
              code
              name
            }
            portSequence
            sailingNights
            totalNights
            type
            ship {
              code
              name
            }
          }
        }
        sailings {
          id
          itinerary {
            name
            code
            voyageType
            days {
              number
              type
              ports {
                activity
                arrivalTime
                departureTime
                port {
                  code
                  name
                  region
                }
              }
            }
            departurePort { code name region }
            destination { code name }
            portSequence
            sailingNights
            totalNights
            type
            ship { code name }
          }
          sailDate
          startDate
          endDate
          bookingLink
        }
      }
      total
    }
  }
}
'@

$body = @{
  operationName = "cruiseSearch_CruisesRiver"
  variables = @{
    filters = "voyageType:OCEAN"
    sort = @{ by = "RECOMMENDED" }
    pagination = @{ count = 1000; skip = 0 }
  }
  query = $query
} | ConvertTo-Json -Depth 20 -Compress

$response = Invoke-WebRequest -UseBasicParsing -Uri "https://www.celebritycruises.com/cruises/graph" `
-Method "POST" `
-WebSession $session `
-Headers @{
  "accept"="application/json"
  "accept-language"="en-US,en;q=0.9,fr;q=0.8"
  "apollographql-client-name"="cel-NextGen-Cruise-Search"
  "apollographql-query-name"="cruiseSearch_CruisesRiver"
  "brand"="C"
  "country"="CAN"
  "countryalpha2code"="CA"
  "currency"="CAD"
  "language"="en"
  "office"="MIA"
  "origin"="https://www.celebritycruises.com"
  "referer"="https://www.celebritycruises.com/ca/cruises?country=CAN"
  "request-timeout"="20"
  "skip_authentication"="true"
  "x-session-id"="cb1b18a0-1a22-4593-9c23-aea5dfa03a28"
} `
-ContentType "application/json" `
-Body $body

$response.Content | Set-Content ".\celebrity-voyages-raw.json" -Encoding UTF8

# Quick verification
$json = $response.Content | ConvertFrom-Json
$cruises = $json.data.cruiseSearch.results.cruises
$sailings = @($cruises | ForEach-Object { $_.sailings })
Write-Host "Cruise groups:" $cruises.Count
Write-Host "Individual sailings:" $sailings.Count
Write-Host "API total:" $json.data.cruiseSearch.results.total
Write-Host "Saved: celebrity-voyages-raw.json"


Write-Host ""
Write-Host "Celebrity acquisition complete."
Write-Host "  celebrity-voyages-raw.json"
