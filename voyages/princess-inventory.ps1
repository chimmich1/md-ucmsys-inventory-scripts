$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("coveo_visitorId", "7680e71b-4524-46a3-bc98-a09be3635ea0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("getLocale", "%7B%22expiry%22%3A1788836885%2C%22timestamp%22%3A1788664085%2C%22ttl%22%3A172800%2C%22zipCode%22%3A%22K0H%22%2C%22ipAddress%22%3A%22142.113.239.5%22%2C%22status%22%3A%22US%22%2C%22country%22%3A%22CA%22%2C%22countryPhone%22%3A%221-800-774-6237%22%2C%22specialOffers%22%3A%22true%22%2C%22brochures%22%3A%22true%22%2C%22lastUpdated%22%3A%221788664085%22%2C%22regionCode%22%3A%22ON%22%2C%22timezone%22%3A%22EST%22%2C%22defaultHomeCity%22%3A%22YVR%22%2C%22primaryCurrency%22%3A%22CAD%22%2C%22secondaryCurrency%22%3A%22USD%22%2C%22aircity%22%3A%22YVR%22%2C%22isEU%22%3A%22false%22%2C%22isIntl%22%3Atrue%7D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dw_dnt", "0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("osano_consentmanager_uuid", "7cbb4c5a-b4f4-4366-82f2-e634ce25d047", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("osano_consentmanager", "ilvzL0F1yP2dVufJ7nFK-BD6V0bezpSAM1bfkii08oXRBTSAWidlE0ArJGpuitgB6-TqRhHGn6EPasaxRIfIFSe8RDAui73A-1n5A-Yk7-buHWEPOigs5Ai4RRJt9zqEWuCGFkEJYsVPBHH29SCjtFv5nWdCDKwbt1PX_HQ2dIPlhrF1gqjXDVZFLWoPuB_dsh6c6b_HM7jBFhdvqvjmtd53Y2rQchQ0Sn8lc4trx2rgwEP10dLlUmI7tG-F9XKR0prOAkduL_9GSZ_DBJk-rPRPIDYI8wXOmtYUNvfLoA5_0B0qOiaCEFYQ1U--Qy5sgivhsyojWsA=", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("OsanoAlertBoxClosed", "2026-09-06T03%3A08%3A07.010Z", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rxVisitor", "1788664087256GR0I22NIDT74CD4T3II6229F3PP0B9D9", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ecid", "MCMID%7C61989789297361152271876970136432755444", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("optimizelyEndUserId", "oeu1788664087482r0.3787233932232379", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_gcl_au", "1.1.4762988.1788664088", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_mibhv", "anon-1788664087730-5419018038_6160", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_id", "1df35024a2114de5bc10b0fe5664e4c5", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_attn_", "eyJ1Ijoie1wiY29cIjoxNzg4NjY0MDg3OTMxLFwidW9cIjoxNzg4NjY0MDg3OTMxLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjFkZjM1MDI0YTIxMTRkZTViYzEwYjBmZTU2NjRlNGM1XCJ9In0=", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_cco", "1788664087933", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_fbp", "fb.1.1788664087974.451890982694107831", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_tt_enable_cookie", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ttp", "01M1TB01GJN85YEQ3KVKHKHP55_.tt.1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga", "GA1.1.762381982.1788664088", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_pin_unauth", "dWlkPVl6UXhZVEEzT0dNdFltWmhOaTAwTVdFNUxXSXdOMlF0TW1Wa05qUTBaVGRpWWpjMA", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl_langSelected", "jp", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PR_gts_svc_princess_lbl", "1796440374~rv=41~id=efa8e6bc8855b3e5df4a53a5140b5973", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_up", "1.2.417214122.1788664375", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_rdt_uuid", "1788664087642.42b07616-b082-4aa4-a322-76bb8fa84483", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_rdt_em", ":bff331b4cf57374e52bf153731f1f39c5d69f0843e02d93a8c7d09028407c2ba", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("RT", "`"z=1&dm=princess.com&si=d3b9fcaa-738e-4197-b3a9-251b87554a42&ss=mtp8lmmy&sl=0&tt=0&bcn=%2F%2F68794906.akstat.io%2F&hd=3l1aa`"", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("COOKIE_CHECK", "YES", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl-guestSession", "%7B%22sessionID%22%3A1788762267%7D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akaalb_prod_gw_api_princess", "~op=gw_api_princess_prod:prod_gw_api_default|~rv=35~m=prod_gw_api_default:0|~os=65760bbfddf7b582d215068ad3be04be~id=6324ad78bbfde84f20ff6ae075f94444", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl_systemOutage", "false", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PR_princess_aws_api_gw_lbl", "3966215066~rv=93~id=da8185fd7ef2b9d380822584c9d33a7f", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "BB56C025A3E9490B689DE68B9BF91542~000000000000000000000000000000~YAAQlX86F3rtJFGgAQAANyKKegEWYssobnpgzfm+uz5YHMztDdtFoX9qb7tw+ZAJedGfhnBPtbzS6+SgWGpbJ6EO4/en81zwAH2YyAUrrhQYOhzOXcy88D0pAM30l/DlAzORjx9bC9EFI+15NGuGGqeo0GPHlbaBE6ryWtf2iBQZWFNWiIEXanMKwODjTyEylCxSPp9PYuL66TowZjFVbYBO+XckWnqiqpEuztcdaLUjLzIpPDrzuyVW7GQR6q1f5ePa5/Cd+fXTqP/iDnQDAbWeRF1k2Sl6XkSRzHsSq1zhTPRpXEe8WFFITcprjykaSi+qo9gkbdy0j4RxUJCKMVO/Cmq1zDGtHKmJuFWz+uWwso/mfiRhyezJt0nRJz6ie+l0mFM87CY=", "/", ".api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akaalb_prod_gts_svc_princess", "~op=gts_svc_princess_prod:prod_gts_svc_default|~rv=20~m=prod_gts_svc_default:0|~os=00dfaab00c14898add27ece504771b45~id=8e56332b2f8635ff1d4c1c93f3cadf5a", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtSa", "-", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("optimizelySession", "0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_vnc365", "1820298305700%26vn%3D3", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ivc", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kndctr_21C91F2F575539D07F000101_AdobeOrg_identity", "CiY2MTk4OTc4OTI5NzM2MTE1MjI3MTg3Njk3MDEzNjQzMjc1NTQ0NFIQCIKGwKWHNBgBKgNWQTYwA6ABhobApYc08AGA6qrUhzQ%3D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kndctr_21C91F2F575539D07F000101_AdobeOrg_cluster", "va6", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCVS_21C91F2F575539D07F000101%40AdobeOrg", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCV_21C91F2F575539D07F000101%40AdobeOrg", "179643557%7CMCMID%7C61989789297361152271876970136432755444%7CMCAAMLH-1789367105%7C7%7CMCAAMB-1789367105%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1788769505s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0%7CMCIDTS%7C20703", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppn", "gb-www%3A%2Fcruise-search%2Fsearch%2F", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gds_s", "Less%20than%207%20days", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_vnum", "1790827200590%26vn%3D3", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_invisit", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_cc", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_session_id", "bd6789803a4c4e039c6f861cf4c2e6ce", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_utm_param_source", "chatgpt.com", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_dv", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_ss_referrer", "ORGANIC", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtCookie", "v_4_srv_1_sn_7803C1D8DB531BB2A661CABBFD51C8B3_app-3Aea7c4b59f27d43eb_1_app-3A84746b1bc55b6714_1_ol_0_perc_100000_mul_1_rcs-3Acss_0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_tp", "9026", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "5DF6995DB8834165C5E4938037186EF6~000000000000000000000000000000~YAAQDGI0F8ifEkygAQAA52yMegHEBa2d8R5y/WsTzvx2xvTxalGLOAoASJjxtOhkxbzch/MYEkQMsYU/+FUyinjdXZBQeCOZasA2C68/1fU/sBtdQFOwFCosOWSI9/E3GzQ9qtaaQDnc/pw/5KcBBJ6EmSUqqUSCr0H3vK1GsRapMr5iCn59THS2NUYUumCHyVVSSVCxxJBLOvADUE1+2OzDmDFPEGbT6BSIHshSYI2uwCoPy2+Dm2KpZuaXaEtGWG4AmQ94htYhKxvh1RchofGY5CjpZ+ChhmwcnDSsyqsL01A46zD979aayNhJh9uvOTtPfdCWW3OIDjGsh96FJLP2PhAPFIjPSJzwBFL3fg==", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_nr30", "1788762418803-Repeat", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_nr", "1788762418918-Repeat", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gds", "1788762418919", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppv", "gb-www%253A%2Fcruise-search%2Fsearch%2F%2C12%2C12%2C1113", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetsid", "dde27f60aa8411f18c8451982d64c818", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetvid", "2f3ffa60a9a011f19e77d56d41f56c21", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_pv", "2", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid", "1788762306102::jrRg3nhFre4QwBCALnKG.3.1788762419813.0::1.109594.113368::94998.1.1194.101::0.0.0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid_C9PEBK3C77UE268EPMK0", "1788762306101::NdrhJwTgWXcJYZF5ly_9.3.1788762419814.1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AKA_A2", "A", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_6Q2QYXFR29", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_51RPCJ1HFX", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_4S9XKY4D84", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_DYQWS5L2MB", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_TJ8N0H2JBC", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_Z982QBQJ84", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h197458848", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rxvt", "1788764231592|1788762305292", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtPC", "1`$162431582_913h-vPDJVIABFABFLUIHHUKAPHWRPPRKWIKED-0e0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("fs_lua", "1.1788762431608", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("fs_uid", "#o-20RRHV-na1#861fa265-4152-45dc-8d46-6be53f23305e:5d613679-624a-422f-869c-b2145b47fb04:1788762431608::1####/1820200105", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_abck", "187D67DB2F2D3A5CF39BEA2F58B1CABF~-1~YAAQlX86F3MLJVGgAQAAB6OMehBXF1yOe22pm53zYkX5Sh9zdIIfS1oQd4b1u+F0B1eqRlQOsHTsAuq9K8xVsTeSPfDj8twdOYApnLZgnQbTcLKu3OPJQXovTyhaAffTUVoFjMfFwxtYRzMUn+HXvxVudgyVoucv5cMZCYvnmLBqNboMgHy6QlNKH0FsgiOWAOOd6kWZhT6n920RmkKHxoy0rK2qKFsmfqxmt/A8/9VHe+EZpT9R3XcYf1qMAv4cA2zFYCj1die0kTXJkUdQNL9DnIUiqJprazbelAEuRWvWzjjCWormnNydtNIZSsJCfAKPH6N/FXy+GUIjMGlIACW3+eTqzwNsFfiyUeZK2in7BCswZidK5T4c7i9hwXIDXa0nM5AJjWhbE2GjoyvOPEBHoTFdZUki3ORrYhkpyASc6E6a/7nf9RRz6vC1LmMA+EdcqQwltep5krL0jFAnzl44iLXKdlyvWXeU6cZmpe3TINfVuFK8rDDNtVcccL0bi6xRWj5joB5HCRETef4hRpnnU7rx0b7zHAJqI2qEijYn7ZnUFY9+Z+pFkXyEwph1BpmOcWQV7aKXS96gseEG2WEauTaRYjCMANPVAdqdD4mPMqMI3GLUJM9NiRcMRyBYlTsmmuSgUEYAEzI3esGZXdru4RUThxxYWGzoqdR04idbrg65IlnKANGIlQkX0iqiXMSTyERoYf5Svmy61x/1AeRt8aQPINEARnURgwOeTfTZTyUuUqa9rOif7+dn8fgNJHIEU7Rh4nhb3ExDDPU3pZwnAD4OYWKwUqOCRBizrUt2DyQINssndj2mh9+vBbXWUsdxjSLwCPROO0NkSUztuL2GwnWJy/7BEMTtOhXmsTCCG8Tbutomh1VlTQC6LqPRogWWaYwDM4Q61GHuanGBA0X+zGEEPUvV7j/TWTpdOSU+3oU0bAX9P4Q48Wr+cGN93YZ3Zt4kLG/3B+dwFR7GrAW7rxPsf+HW7VzF0Kwk0CZ1XoZesczD57LYgFOdQYyYdbWkWL090lEJWeZfGwywy/M2gfnKGiSWYfCZKfprK1YzwNJ9d0yYSMZrNx4KGRIRHeipnFBrXLma7Z4=~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f8l4jEgdRVrARhez3UPwQP7z7ZjBDFbwd7katiAbzuExBWsR5aJXfH8hJedPRHKkTfEHl8WucKu9I0oe8O+geMyNefmJqDdfn9pH~-1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sz", "0B89ADF746CC476B745638E401823E84~YAAQlX86F3ULJVGgAQAAB6OMegHCxTprZeh45Y0FFcqISBhx739dFyQMqSfyTmZWciK7pkP3AxbWepAwVHOLFOWzdqXJYhGE+rZa0rgmlYed4h/Wd7d/OCK5f4RJ/Vm3QL8GBTKDJhgjM6MVyPcttt+QlTylwx3brlVmu+60/WctmYLKtJ0V7yY0xAudwuXDr50DnVe+NcoSvbrMoC3/37p1tiwQBW0l2nkg5o71hVOUW0N+iAt6+1vtUUuOjfEBvNl5GDrKZVeqKChkyekFRL+y3kcsM+TEE52nqsmw3XEjv0wp6JbJbu7VomnywFAOYn67ZLePfNZxwuNxdTNpSGZEeaHVT7EdtQeZLdMLG6M4jas6uRRlrr6qH+5pbow7wx5/pBgX/zGWe/bTtMksG1ZgfkpIX5EkEXxs8pt6cJ4=~4277317~4273989", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sv", "041667D014B80C1E8AAB2A16504202E3~YAAQlX86F5sLJVGgAQAAz6WMegEvoJKy7h8PdQR1fljYrsajGCfC4ue0gabp241VDZ8nTjs9dRGKWuJwJUqPO1a53Gclb6xUDSah3PhcK//1UxdVROV/hXc+n2RxXretaQwi0+DScCSmUGgzcniIt93YLFnM/AzoYldLKxmTGvogJET92EPBZH94IUwnIWv7MQB64mWn8XnCO51rQJLIZRxSc1BtUZAWmNnJF1LSTIMAUxCHP+OAM6fLauJ/5DJk6W7wh/65yw==~1", "/", ".api.princess.com")))
$response = Invoke-WebRequest -UseBasicParsing -Uri "https://gw.api.princess.com/pcl-web/internal/resdb/p1.0/products?agencyCountry=CA&cruiseType=C&voyageStatus=A&webDisplay=Y&promoFilter=all&light=false" `
-WebSession $session `
-Headers @{
"authority"="gw.api.princess.com"
  "method"="GET"
  "path"="/pcl-web/internal/resdb/p1.0/products?agencyCountry=CA&cruiseType=C&voyageStatus=A&webDisplay=Y&promoFilter=all&light=false"
  "scheme"="https"
  "accept"="application/json, text/plain, */*"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="en-US,en;q=0.9,fr;q=0.8"
  "appid"="{`"agencyId`":`"DIRPB`",`"cruiseLineCode`":`"PCL`",`"sessionId`":`"3a98e5e8-2c43-4b34-ac8f-f27ae6786df3`",`"systemId`":`"PB`",`"gdsCookie`":`"CO=CA`"}"
  "bookingcompany"="PC"
  "origin"="https://www.princess.com"
  "pcl-client-id"="32e7224ac6cc41302f673c5f5d27b4ba"
  "priority"="u=1, i"
  "productcompany"="PC"
  "referer"="https://www.princess.com/"
  "reqsrc"="W"
  "sec-ch-ua"="`"Chromium`";v=`"152`", `"Not?A_Brand`";v=`"24`", `"Google Chrome`";v=`"152`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-site"
  "x-pcl-traceapp"="NA=pcl-ube-ui"
}
$response.Content |
    Set-Content ".\princess-products.json" -Encoding UTF8
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("coveo_visitorId", "7680e71b-4524-46a3-bc98-a09be3635ea0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("getLocale", "%7B%22expiry%22%3A1788836885%2C%22timestamp%22%3A1788664085%2C%22ttl%22%3A172800%2C%22zipCode%22%3A%22K0H%22%2C%22ipAddress%22%3A%22142.113.239.5%22%2C%22status%22%3A%22US%22%2C%22country%22%3A%22CA%22%2C%22countryPhone%22%3A%221-800-774-6237%22%2C%22specialOffers%22%3A%22true%22%2C%22brochures%22%3A%22true%22%2C%22lastUpdated%22%3A%221788664085%22%2C%22regionCode%22%3A%22ON%22%2C%22timezone%22%3A%22EST%22%2C%22defaultHomeCity%22%3A%22YVR%22%2C%22primaryCurrency%22%3A%22CAD%22%2C%22secondaryCurrency%22%3A%22USD%22%2C%22aircity%22%3A%22YVR%22%2C%22isEU%22%3A%22false%22%2C%22isIntl%22%3Atrue%7D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dw_dnt", "0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("osano_consentmanager_uuid", "7cbb4c5a-b4f4-4366-82f2-e634ce25d047", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("osano_consentmanager", "ilvzL0F1yP2dVufJ7nFK-BD6V0bezpSAM1bfkii08oXRBTSAWidlE0ArJGpuitgB6-TqRhHGn6EPasaxRIfIFSe8RDAui73A-1n5A-Yk7-buHWEPOigs5Ai4RRJt9zqEWuCGFkEJYsVPBHH29SCjtFv5nWdCDKwbt1PX_HQ2dIPlhrF1gqjXDVZFLWoPuB_dsh6c6b_HM7jBFhdvqvjmtd53Y2rQchQ0Sn8lc4trx2rgwEP10dLlUmI7tG-F9XKR0prOAkduL_9GSZ_DBJk-rPRPIDYI8wXOmtYUNvfLoA5_0B0qOiaCEFYQ1U--Qy5sgivhsyojWsA=", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("OsanoAlertBoxClosed", "2026-09-06T03%3A08%3A07.010Z", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rxVisitor", "1788664087256GR0I22NIDT74CD4T3II6229F3PP0B9D9", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ecid", "MCMID%7C61989789297361152271876970136432755444", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("optimizelyEndUserId", "oeu1788664087482r0.3787233932232379", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_gcl_au", "1.1.4762988.1788664088", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_mibhv", "anon-1788664087730-5419018038_6160", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_id", "1df35024a2114de5bc10b0fe5664e4c5", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_attn_", "eyJ1Ijoie1wiY29cIjoxNzg4NjY0MDg3OTMxLFwidW9cIjoxNzg4NjY0MDg3OTMxLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjFkZjM1MDI0YTIxMTRkZTViYzEwYjBmZTU2NjRlNGM1XCJ9In0=", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_cco", "1788664087933", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_fbp", "fb.1.1788664087974.451890982694107831", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_tt_enable_cookie", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ttp", "01M1TB01GJN85YEQ3KVKHKHP55_.tt.1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga", "GA1.1.762381982.1788664088", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_pin_unauth", "dWlkPVl6UXhZVEEzT0dNdFltWmhOaTAwTVdFNUxXSXdOMlF0TW1Wa05qUTBaVGRpWWpjMA", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl_langSelected", "jp", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PR_gts_svc_princess_lbl", "1796440374~rv=41~id=efa8e6bc8855b3e5df4a53a5140b5973", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_up", "1.2.417214122.1788664375", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_rdt_uuid", "1788664087642.42b07616-b082-4aa4-a322-76bb8fa84483", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_rdt_em", ":bff331b4cf57374e52bf153731f1f39c5d69f0843e02d93a8c7d09028407c2ba", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("RT", "`"z=1&dm=princess.com&si=d3b9fcaa-738e-4197-b3a9-251b87554a42&ss=mtp8lmmy&sl=0&tt=0&bcn=%2F%2F68794906.akstat.io%2F&hd=3l1aa`"", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("COOKIE_CHECK", "YES", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl-guestSession", "%7B%22sessionID%22%3A1788762267%7D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akaalb_prod_gw_api_princess", "~op=gw_api_princess_prod:prod_gw_api_default|~rv=35~m=prod_gw_api_default:0|~os=65760bbfddf7b582d215068ad3be04be~id=6324ad78bbfde84f20ff6ae075f94444", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl_systemOutage", "false", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PR_princess_aws_api_gw_lbl", "3966215066~rv=93~id=da8185fd7ef2b9d380822584c9d33a7f", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "BB56C025A3E9490B689DE68B9BF91542~000000000000000000000000000000~YAAQlX86F3rtJFGgAQAANyKKegEWYssobnpgzfm+uz5YHMztDdtFoX9qb7tw+ZAJedGfhnBPtbzS6+SgWGpbJ6EO4/en81zwAH2YyAUrrhQYOhzOXcy88D0pAM30l/DlAzORjx9bC9EFI+15NGuGGqeo0GPHlbaBE6ryWtf2iBQZWFNWiIEXanMKwODjTyEylCxSPp9PYuL66TowZjFVbYBO+XckWnqiqpEuztcdaLUjLzIpPDrzuyVW7GQR6q1f5ePa5/Cd+fXTqP/iDnQDAbWeRF1k2Sl6XkSRzHsSq1zhTPRpXEe8WFFITcprjykaSi+qo9gkbdy0j4RxUJCKMVO/Cmq1zDGtHKmJuFWz+uWwso/mfiRhyezJt0nRJz6ie+l0mFM87CY=", "/", ".api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akaalb_prod_gts_svc_princess", "~op=gts_svc_princess_prod:prod_gts_svc_default|~rv=20~m=prod_gts_svc_default:0|~os=00dfaab00c14898add27ece504771b45~id=8e56332b2f8635ff1d4c1c93f3cadf5a", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtSa", "-", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("optimizelySession", "0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_vnc365", "1820298305700%26vn%3D3", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ivc", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kndctr_21C91F2F575539D07F000101_AdobeOrg_identity", "CiY2MTk4OTc4OTI5NzM2MTE1MjI3MTg3Njk3MDEzNjQzMjc1NTQ0NFIQCIKGwKWHNBgBKgNWQTYwA6ABhobApYc08AGA6qrUhzQ%3D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kndctr_21C91F2F575539D07F000101_AdobeOrg_cluster", "va6", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCVS_21C91F2F575539D07F000101%40AdobeOrg", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCV_21C91F2F575539D07F000101%40AdobeOrg", "179643557%7CMCMID%7C61989789297361152271876970136432755444%7CMCAAMLH-1789367105%7C7%7CMCAAMB-1789367105%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1788769505s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0%7CMCIDTS%7C20703", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppn", "gb-www%3A%2Fcruise-search%2Fsearch%2F", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gds_s", "Less%20than%207%20days", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_vnum", "1790827200590%26vn%3D3", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_invisit", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_cc", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_session_id", "bd6789803a4c4e039c6f861cf4c2e6ce", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_utm_param_source", "chatgpt.com", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_dv", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_ss_referrer", "ORGANIC", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtCookie", "v_4_srv_1_sn_7803C1D8DB531BB2A661CABBFD51C8B3_app-3Aea7c4b59f27d43eb_1_app-3A84746b1bc55b6714_1_ol_0_perc_100000_mul_1_rcs-3Acss_0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_tp", "9026", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "5DF6995DB8834165C5E4938037186EF6~000000000000000000000000000000~YAAQDGI0F8ifEkygAQAA52yMegHEBa2d8R5y/WsTzvx2xvTxalGLOAoASJjxtOhkxbzch/MYEkQMsYU/+FUyinjdXZBQeCOZasA2C68/1fU/sBtdQFOwFCosOWSI9/E3GzQ9qtaaQDnc/pw/5KcBBJ6EmSUqqUSCr0H3vK1GsRapMr5iCn59THS2NUYUumCHyVVSSVCxxJBLOvADUE1+2OzDmDFPEGbT6BSIHshSYI2uwCoPy2+Dm2KpZuaXaEtGWG4AmQ94htYhKxvh1RchofGY5CjpZ+ChhmwcnDSsyqsL01A46zD979aayNhJh9uvOTtPfdCWW3OIDjGsh96FJLP2PhAPFIjPSJzwBFL3fg==", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_nr30", "1788762418803-Repeat", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_nr", "1788762418918-Repeat", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gds", "1788762418919", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppv", "gb-www%253A%2Fcruise-search%2Fsearch%2F%2C12%2C12%2C1113", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetsid", "dde27f60aa8411f18c8451982d64c818", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetvid", "2f3ffa60a9a011f19e77d56d41f56c21", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_pv", "2", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid", "1788762306102::jrRg3nhFre4QwBCALnKG.3.1788762419813.0::1.109594.113368::94998.1.1194.101::0.0.0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid_C9PEBK3C77UE268EPMK0", "1788762306101::NdrhJwTgWXcJYZF5ly_9.3.1788762419814.1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AKA_A2", "A", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_6Q2QYXFR29", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_51RPCJ1HFX", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_4S9XKY4D84", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_DYQWS5L2MB", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_TJ8N0H2JBC", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_Z982QBQJ84", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h197458848", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rxvt", "1788764231592|1788762305292", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtPC", "1`$162431582_913h-vPDJVIABFABFLUIHHUKAPHWRPPRKWIKED-0e0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("fs_lua", "1.1788762431608", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("fs_uid", "#o-20RRHV-na1#861fa265-4152-45dc-8d46-6be53f23305e:5d613679-624a-422f-869c-b2145b47fb04:1788762431608::1####/1820200105", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_abck", "187D67DB2F2D3A5CF39BEA2F58B1CABF~-1~YAAQj386F5NWaVagAQAAqaaMehAZ/KJmNZEcWLoEwxrdtIEc9ZF6y+840BOvfD7PdIxrSOgmPhkXYRIay8r4JWdMSpGNjGVoU3OtL8jsncRPCGTX5v43PDhdxY51wkN1zD0A3+7YnBlddkZXFz/DrJVSVC59WV+js4ZthODRbVT5jfPfu9k7YSvqyVUQNfx4JDhsfPuD4Aw5fPG44pxnj3liIv/VTLH8/j8bDnqyZUzJjnU8875FpCkP+j2dTcaKz18gVsWiD2apEMhyrMoXnUZxgeHFcfZRZITMd5rToNmTC0VfCJigYDcUtPp1ttNPbRBc61kXT9UcgwoSS65dasjTg9HshbwJ7FzXcG0DhA913ZxY46YLA9cR1N8HoNEjbA1KhdSxLe7YVKoTfjIeq2KxFvicKmQ6JFv7dGZgE7hAfMv0ON5x++IDpJn02UZh1qv85/COUTDKtmzPEKibcMfVAUr6PD544JNG3WnmVc8lgHFQDynKWgSIagFRA9Bahkd8th4Qs20DU2DvnHoVrTVonLLkg/R3+UqYANl+8TdCbPzN/SmTvWDJn3JIGcowuZ5l4wad1ma6ZW0tZRGXYZ+AdwBTZ1du6KFvv80ml5nFYqH4Q8Th41Cjj6/xaObsmqea8UaE5b8BWtcOFQeyhU/CvPClcr5BBI+HNNduUKhoPEQM5sxYttvDAX/Sj/dc31Z70RI5sw/Iwr+i/DWo8r2Ai47PuAKRRwXq5aI7+e6QEDV4CoJM2Frl2GkFPdi8R6JGEclMbG8jka3u0UC5PJLOcrL0uvV4UgS5TKIZyYYB6QxT18trXUxZRqWZqB5QAkIiqosauUJmxLpAomjm6ktZQJIhnwOdkma7dyqMr3S1Sy+4F7rHOyb8Dw1BUEy6Kcp0x3EjXNy/VIOcphbdaPFjOpOAS90/dDffCTfkcxpz2O86Xej+/y0o7lkMPUbNLOpsMFUTV4IL/b9sJjvAIle0Jj2aKtwRBFBEzLRMOrUeJrYFrlrHYnbynhUAb17snXbrMnZGYVrNg8GBBctSyg7vPLC0k49Nd9lrhgnkmFcwYmK9oM3abSK03Ta6U7PX7QyB102rD4lnuUrBgvXvf+kycrVYfBJ61q6oWFg5jxVi4MZtGk2QnBCj8uD0q0p+CxXObnuhzQ==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f8l4jEgdRVrARhez3UPwQP7z7ZjBDFbwd7katiAbzuExBWsR5aJXfH8hJedPRHKkTfEHl8WucKu9I0oe8O+geMyNefmJqDdfn9pH~-1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sz", "0B89ADF746CC476B745638E401823E84~YAAQj386F5RWaVagAQAAqaaMegHmxP+yQCDEv4Ai0YwnWzX/0mK7UbXEnd0kriP0/JpB8bpUtSQ6dJBgOezsFywoWUiBQxicuAB8xcjAJtN6/JRr44uB+fE2Z/m4f3fvZRVFPI+A1wsV64fwn0PbDnwJy3l1csWMMhWql3ER4mqKCZ7Jl7mtQfuJH3kUwER+oULtPTMf9pkCytTN4Hqaq33lu/PsAG4waxTBtYlVbGLEgpM3QpJOhlVyGTCgT3atsdcEkKIwdJKh1dTKWyAzqWAn9xHs4yWQ3ox9Dq9oHZn41uEzNntV8mjF+iDmcQM0DbG+YARMONCsc33b+tj3cMaInsVO6OHZfxtkdY2FdS+d4QzJviyEmGgmhnuHL61diK8mBlt36uAjbLdvf3ZyqWCWXyObsBTkWsGBKEorEmSi66EfGQ==~4277317~4273989", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sv", "041667D014B80C1E8AAB2A16504202E3~YAAQlX86F7MLJVGgAQAAJaiMegGymj1qo84i7VNtbo7ArWbrKBgYoi/pEZ1IMZxJtVgXElCfTAMYDR2g3gRX9tkWUAjCa+it7/JU4Pe8rvUqcdMwRCBYYstITCnoqY8Lt6jryx7DXMlLS1RsFtx2bjgDj7CpSDNLcy8+E28TA5VKwfYH8imvyGE2bNa82BMp6AkbjO7GZNHwTo8tn/P5M+cFHNWkciAmYp6ADhIr3HVEtNGAIHjD+wV4jzGVt2cNq2weFjFzDA==~1", "/", ".api.princess.com")))
$response = Invoke-WebRequest -UseBasicParsing -Uri "https://gw.api.princess.com/pcl-web/internal/resdb/p1.0/ports" `
-WebSession $session `
-Headers @{
"authority"="gw.api.princess.com"
  "method"="GET"
  "path"="/pcl-web/internal/resdb/p1.0/ports"
  "scheme"="https"
  "accept"="application/json, text/plain, */*"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="en-US,en;q=0.9,fr;q=0.8"
  "appid"="{`"agencyId`":`"DIRPB`",`"cruiseLineCode`":`"PCL`",`"sessionId`":`"3a98e5e8-2c43-4b34-ac8f-f27ae6786df3`",`"systemId`":`"PB`",`"gdsCookie`":`"CO=CA`"}"
  "bookingcompany"="PC"
  "origin"="https://www.princess.com"
  "pcl-client-id"="32e7224ac6cc41302f673c5f5d27b4ba"
  "priority"="u=1, i"
  "productcompany"="PC"
  "referer"="https://www.princess.com/"
  "reqsrc"="W"
  "sec-ch-ua"="`"Chromium`";v=`"152`", `"Not?A_Brand`";v=`"24`", `"Google Chrome`";v=`"152`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-site"
  "x-pcl-traceapp"="NA=pcl-ube-ui"
}
$response.Content |
    Set-Content ".\princess-ports.json" -Encoding UTF8

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("coveo_visitorId", "7680e71b-4524-46a3-bc98-a09be3635ea0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("getLocale", "%7B%22expiry%22%3A1788836885%2C%22timestamp%22%3A1788664085%2C%22ttl%22%3A172800%2C%22zipCode%22%3A%22K0H%22%2C%22ipAddress%22%3A%22142.113.239.5%22%2C%22status%22%3A%22US%22%2C%22country%22%3A%22CA%22%2C%22countryPhone%22%3A%221-800-774-6237%22%2C%22specialOffers%22%3A%22true%22%2C%22brochures%22%3A%22true%22%2C%22lastUpdated%22%3A%221788664085%22%2C%22regionCode%22%3A%22ON%22%2C%22timezone%22%3A%22EST%22%2C%22defaultHomeCity%22%3A%22YVR%22%2C%22primaryCurrency%22%3A%22CAD%22%2C%22secondaryCurrency%22%3A%22USD%22%2C%22aircity%22%3A%22YVR%22%2C%22isEU%22%3A%22false%22%2C%22isIntl%22%3Atrue%7D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dw_dnt", "0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("osano_consentmanager_uuid", "7cbb4c5a-b4f4-4366-82f2-e634ce25d047", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("osano_consentmanager", "ilvzL0F1yP2dVufJ7nFK-BD6V0bezpSAM1bfkii08oXRBTSAWidlE0ArJGpuitgB6-TqRhHGn6EPasaxRIfIFSe8RDAui73A-1n5A-Yk7-buHWEPOigs5Ai4RRJt9zqEWuCGFkEJYsVPBHH29SCjtFv5nWdCDKwbt1PX_HQ2dIPlhrF1gqjXDVZFLWoPuB_dsh6c6b_HM7jBFhdvqvjmtd53Y2rQchQ0Sn8lc4trx2rgwEP10dLlUmI7tG-F9XKR0prOAkduL_9GSZ_DBJk-rPRPIDYI8wXOmtYUNvfLoA5_0B0qOiaCEFYQ1U--Qy5sgivhsyojWsA=", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("OsanoAlertBoxClosed", "2026-09-06T03%3A08%3A07.010Z", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rxVisitor", "1788664087256GR0I22NIDT74CD4T3II6229F3PP0B9D9", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ecid", "MCMID%7C61989789297361152271876970136432755444", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("optimizelyEndUserId", "oeu1788664087482r0.3787233932232379", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_gcl_au", "1.1.4762988.1788664088", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_mibhv", "anon-1788664087730-5419018038_6160", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_id", "1df35024a2114de5bc10b0fe5664e4c5", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_attn_", "eyJ1Ijoie1wiY29cIjoxNzg4NjY0MDg3OTMxLFwidW9cIjoxNzg4NjY0MDg3OTMxLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjFkZjM1MDI0YTIxMTRkZTViYzEwYjBmZTU2NjRlNGM1XCJ9In0=", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_cco", "1788664087933", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_fbp", "fb.1.1788664087974.451890982694107831", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_tt_enable_cookie", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ttp", "01M1TB01GJN85YEQ3KVKHKHP55_.tt.1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga", "GA1.1.762381982.1788664088", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_pin_unauth", "dWlkPVl6UXhZVEEzT0dNdFltWmhOaTAwTVdFNUxXSXdOMlF0TW1Wa05qUTBaVGRpWWpjMA", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl_langSelected", "jp", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PR_gts_svc_princess_lbl", "1796440374~rv=41~id=efa8e6bc8855b3e5df4a53a5140b5973", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_up", "1.2.417214122.1788664375", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_rdt_uuid", "1788664087642.42b07616-b082-4aa4-a322-76bb8fa84483", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_rdt_em", ":bff331b4cf57374e52bf153731f1f39c5d69f0843e02d93a8c7d09028407c2ba", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("RT", "`"z=1&dm=princess.com&si=d3b9fcaa-738e-4197-b3a9-251b87554a42&ss=mtp8lmmy&sl=0&tt=0&bcn=%2F%2F68794906.akstat.io%2F&hd=3l1aa`"", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("COOKIE_CHECK", "YES", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl-guestSession", "%7B%22sessionID%22%3A1788762267%7D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akaalb_prod_gw_api_princess", "~op=gw_api_princess_prod:prod_gw_api_default|~rv=35~m=prod_gw_api_default:0|~os=65760bbfddf7b582d215068ad3be04be~id=6324ad78bbfde84f20ff6ae075f94444", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("pcl_systemOutage", "false", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akacd_PR_princess_aws_api_gw_lbl", "3966215066~rv=93~id=da8185fd7ef2b9d380822584c9d33a7f", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "BB56C025A3E9490B689DE68B9BF91542~000000000000000000000000000000~YAAQlX86F3rtJFGgAQAANyKKegEWYssobnpgzfm+uz5YHMztDdtFoX9qb7tw+ZAJedGfhnBPtbzS6+SgWGpbJ6EO4/en81zwAH2YyAUrrhQYOhzOXcy88D0pAM30l/DlAzORjx9bC9EFI+15NGuGGqeo0GPHlbaBE6ryWtf2iBQZWFNWiIEXanMKwODjTyEylCxSPp9PYuL66TowZjFVbYBO+XckWnqiqpEuztcdaLUjLzIpPDrzuyVW7GQR6q1f5ePa5/Cd+fXTqP/iDnQDAbWeRF1k2Sl6XkSRzHsSq1zhTPRpXEe8WFFITcprjykaSi+qo9gkbdy0j4RxUJCKMVO/Cmq1zDGtHKmJuFWz+uWwso/mfiRhyezJt0nRJz6ie+l0mFM87CY=", "/", ".api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("akaalb_prod_gts_svc_princess", "~op=gts_svc_princess_prod:prod_gts_svc_default|~rv=20~m=prod_gts_svc_default:0|~os=00dfaab00c14898add27ece504771b45~id=8e56332b2f8635ff1d4c1c93f3cadf5a", "/", "gw.api.princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtSa", "-", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("optimizelySession", "0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_vnc365", "1820298305700%26vn%3D3", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ivc", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kndctr_21C91F2F575539D07F000101_AdobeOrg_identity", "CiY2MTk4OTc4OTI5NzM2MTE1MjI3MTg3Njk3MDEzNjQzMjc1NTQ0NFIQCIKGwKWHNBgBKgNWQTYwA6ABhobApYc08AGA6qrUhzQ%3D", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("kndctr_21C91F2F575539D07F000101_AdobeOrg_cluster", "va6", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCVS_21C91F2F575539D07F000101%40AdobeOrg", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AMCV_21C91F2F575539D07F000101%40AdobeOrg", "179643557%7CMCMID%7C61989789297361152271876970136432755444%7CMCAAMLH-1789367105%7C7%7CMCAAMB-1789367105%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1788769505s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.5.0%7CMCIDTS%7C20703", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppn", "gb-www%3A%2Fcruise-search%2Fsearch%2F", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gds_s", "Less%20than%207%20days", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_vnum", "1790827200590%26vn%3D3", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_invisit", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_cc", "true", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_session_id", "bd6789803a4c4e039c6f861cf4c2e6ce", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_utm_param_source", "chatgpt.com", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_dv", "1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_ss_referrer", "ORGANIC", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtCookie", "v_4_srv_1_sn_7803C1D8DB531BB2A661CABBFD51C8B3_app-3Aea7c4b59f27d43eb_1_app-3A84746b1bc55b6714_1_ol_0_perc_100000_mul_1_rcs-3Acss_0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_tp", "9026", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ak_bmsc", "5DF6995DB8834165C5E4938037186EF6~000000000000000000000000000000~YAAQDGI0F8ifEkygAQAA52yMegHEBa2d8R5y/WsTzvx2xvTxalGLOAoASJjxtOhkxbzch/MYEkQMsYU/+FUyinjdXZBQeCOZasA2C68/1fU/sBtdQFOwFCosOWSI9/E3GzQ9qtaaQDnc/pw/5KcBBJ6EmSUqqUSCr0H3vK1GsRapMr5iCn59THS2NUYUumCHyVVSSVCxxJBLOvADUE1+2OzDmDFPEGbT6BSIHshSYI2uwCoPy2+Dm2KpZuaXaEtGWG4AmQ94htYhKxvh1RchofGY5CjpZ+ChhmwcnDSsyqsL01A46zD979aayNhJh9uvOTtPfdCWW3OIDjGsh96FJLP2PhAPFIjPSJzwBFL3fg==", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_nr30", "1788762418803-Repeat", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_nr", "1788762418918-Repeat", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("gds", "1788762418919", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("s_ppv", "gb-www%253A%2Fcruise-search%2Fsearch%2F%2C12%2C12%2C1113", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetsid", "dde27f60aa8411f18c8451982d64c818", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_uetvid", "2f3ffa60a9a011f19e77d56d41f56c21", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("__attentive_pv", "2", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid", "1788762306102::jrRg3nhFre4QwBCALnKG.3.1788762419813.0::1.109594.113368::94998.1.1194.101::0.0.0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("ttcsid_C9PEBK3C77UE268EPMK0", "1788762306101::NdrhJwTgWXcJYZF5ly_9.3.1788762419814.1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("AKA_A2", "A", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_6Q2QYXFR29", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_51RPCJ1HFX", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_4S9XKY4D84", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_DYQWS5L2MB", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_TJ8N0H2JBC", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_ga_Z982QBQJ84", "GS2.1.s1788762306`$o4`$g1`$t1788762430`$j46`$l0`$h197458848", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("rxvt", "1788764231592|1788762305292", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("dtPC", "1`$162431582_913h-vPDJVIABFABFLUIHHUKAPHWRPPRKWIKED-0e0", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("fs_lua", "1.1788762431608", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("fs_uid", "#o-20RRHV-na1#861fa265-4152-45dc-8d46-6be53f23305e:5d613679-624a-422f-869c-b2145b47fb04:1788762431608::1####/1820200105", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("_abck", "187D67DB2F2D3A5CF39BEA2F58B1CABF~-1~YAAQj386F5NWaVagAQAAqaaMehAZ/KJmNZEcWLoEwxrdtIEc9ZF6y+840BOvfD7PdIxrSOgmPhkXYRIay8r4JWdMSpGNjGVoU3OtL8jsncRPCGTX5v43PDhdxY51wkN1zD0A3+7YnBlddkZXFz/DrJVSVC59WV+js4ZthODRbVT5jfPfu9k7YSvqyVUQNfx4JDhsfPuD4Aw5fPG44pxnj3liIv/VTLH8/j8bDnqyZUzJjnU8875FpCkP+j2dTcaKz18gVsWiD2apEMhyrMoXnUZxgeHFcfZRZITMd5rToNmTC0VfCJigYDcUtPp1ttNPbRBc61kXT9UcgwoSS65dasjTg9HshbwJ7FzXcG0DhA913ZxY46YLA9cR1N8HoNEjbA1KhdSxLe7YVKoTfjIeq2KxFvicKmQ6JFv7dGZgE7hAfMv0ON5x++IDpJn02UZh1qv85/COUTDKtmzPEKibcMfVAUr6PD544JNG3WnmVc8lgHFQDynKWgSIagFRA9Bahkd8th4Qs20DU2DvnHoVrTVonLLkg/R3+UqYANl+8TdCbPzN/SmTvWDJn3JIGcowuZ5l4wad1ma6ZW0tZRGXYZ+AdwBTZ1du6KFvv80ml5nFYqH4Q8Th41Cjj6/xaObsmqea8UaE5b8BWtcOFQeyhU/CvPClcr5BBI+HNNduUKhoPEQM5sxYttvDAX/Sj/dc31Z70RI5sw/Iwr+i/DWo8r2Ai47PuAKRRwXq5aI7+e6QEDV4CoJM2Frl2GkFPdi8R6JGEclMbG8jka3u0UC5PJLOcrL0uvV4UgS5TKIZyYYB6QxT18trXUxZRqWZqB5QAkIiqosauUJmxLpAomjm6ktZQJIhnwOdkma7dyqMr3S1Sy+4F7rHOyb8Dw1BUEy6Kcp0x3EjXNy/VIOcphbdaPFjOpOAS90/dDffCTfkcxpz2O86Xej+/y0o7lkMPUbNLOpsMFUTV4IL/b9sJjvAIle0Jj2aKtwRBFBEzLRMOrUeJrYFrlrHYnbynhUAb17snXbrMnZGYVrNg8GBBctSyg7vPLC0k49Nd9lrhgnkmFcwYmK9oM3abSK03Ta6U7PX7QyB102rD4lnuUrBgvXvf+kycrVYfBJ61q6oWFg5jxVi4MZtGk2QnBCj8uD0q0p+CxXObnuhzQ==~-1~-1~-1~AAQAAAAG%2f%2f%2f%2f%2f8l4jEgdRVrARhez3UPwQP7z7ZjBDFbwd7katiAbzuExBWsR5aJXfH8hJedPRHKkTfEHl8WucKu9I0oe8O+geMyNefmJqDdfn9pH~-1", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sz", "0B89ADF746CC476B745638E401823E84~YAAQj386F5RWaVagAQAAqaaMegHmxP+yQCDEv4Ai0YwnWzX/0mK7UbXEnd0kriP0/JpB8bpUtSQ6dJBgOezsFywoWUiBQxicuAB8xcjAJtN6/JRr44uB+fE2Z/m4f3fvZRVFPI+A1wsV64fwn0PbDnwJy3l1csWMMhWql3ER4mqKCZ7Jl7mtQfuJH3kUwER+oULtPTMf9pkCytTN4Hqaq33lu/PsAG4waxTBtYlVbGLEgpM3QpJOhlVyGTCgT3atsdcEkKIwdJKh1dTKWyAzqWAn9xHs4yWQ3ox9Dq9oHZn41uEzNntV8mjF+iDmcQM0DbG+YARMONCsc33b+tj3cMaInsVO6OHZfxtkdY2FdS+d4QzJviyEmGgmhnuHL61diK8mBlt36uAjbLdvf3ZyqWCWXyObsBTkWsGBKEorEmSi66EfGQ==~4277317~4273989", "/", ".princess.com")))
$session.Cookies.Add((New-Object System.Net.Cookie("bm_sv", "041667D014B80C1E8AAB2A16504202E3~YAAQlX86F7MLJVGgAQAAJaiMegGymj1qo84i7VNtbo7ArWbrKBgYoi/pEZ1IMZxJtVgXElCfTAMYDR2g3gRX9tkWUAjCa+it7/JU4Pe8rvUqcdMwRCBYYstITCnoqY8Lt6jryx7DXMlLS1RsFtx2bjgDj7CpSDNLcy8+E28TA5VKwfYH8imvyGE2bNa82BMp6AkbjO7GZNHwTo8tn/P5M+cFHNWkciAmYp6ADhIr3HVEtNGAIHjD+wV4jzGVt2cNq2weFjFzDA==~1", "/", ".api.princess.com")))
$response = Invoke-WebRequest -UseBasicParsing -Uri "https://gw.api.princess.com/pcl-web/internal/resdb/p1.0/ships" `
-WebSession $session `
-Headers @{
"authority"="gw.api.princess.com"
  "method"="GET"
  "path"="/pcl-web/internal/resdb/p1.0/ships"
  "scheme"="https"
  "accept"="application/json, text/plain, */*"
  "accept-encoding"="gzip, deflate, br, zstd"
  "accept-language"="en-US,en;q=0.9,fr;q=0.8"
  "appid"="{`"agencyId`":`"DIRPB`",`"cruiseLineCode`":`"PCL`",`"sessionId`":`"3a98e5e8-2c43-4b34-ac8f-f27ae6786df3`",`"systemId`":`"PB`",`"gdsCookie`":`"CO=CA`"}"
  "bookingcompany"="PC"
  "origin"="https://www.princess.com"
  "pcl-client-id"="32e7224ac6cc41302f673c5f5d27b4ba"
  "priority"="u=1, i"
  "productcompany"="PC"
  "referer"="https://www.princess.com/"
  "reqsrc"="W"
  "sec-ch-ua"="`"Chromium`";v=`"152`", `"Not?A_Brand`";v=`"24`", `"Google Chrome`";v=`"152`""
  "sec-ch-ua-mobile"="?0"
  "sec-ch-ua-platform"="`"Windows`""
  "sec-fetch-dest"="empty"
  "sec-fetch-mode"="cors"
  "sec-fetch-site"="same-site"
  "x-pcl-traceapp"="NA=pcl-ube-ui"
}

$response.Content |
    Set-Content ".\princess-ships.json" -Encoding UTF8


# ---- All-voyage itinerary collection ---------------------------------------
$products = Get-Content -Raw ".\princess-products.json" | ConvertFrom-Json
$ids = @($products.products.cruises.voyage.id | ForEach-Object { [string]$_ } | Sort-Object -Unique)

$headers = @{
  "accept"="*/*"
  "bookingcompany"="PC"
  "origin"="https://www.princess.com"
  "pcl-client-id"="32e7224ac6cc41302f673c5f5d27b4ba"
  "productcompany"="PC"
  "referer"="https://www.princess.com/"
  "reqsrc"="W"
}

$all = @()
$i = 0
foreach($id in $ids){
  $i++
  Write-Progress -Activity "Princess itineraries" -Status "$i / $($ids.Count)" -PercentComplete (($i*100)/$ids.Count)

  $uri = "https://gw.api.princess.com/pcl-web/internal/resdb/p1.0/itineraries?cruises=$id"
  try {
    $r = Invoke-RestMethod -Uri $uri -Headers $headers -UserAgent $session.UserAgent
    $hit = @($r.cruises | Where-Object { [string]$_.id -eq $id })
    if(!$hit){
      $uri += "&voyageCode=$id"
      $r = Invoke-RestMethod -Uri $uri -Headers $headers -UserAgent $session.UserAgent
      $hit = @($r.cruises | Where-Object { [string]$_.id -eq $id })
    }
    if($hit){ $all += $hit }
  }
  catch {
    Write-Warning "Itinerary $id failed: $($_.Exception.Message)"
  }
}
Write-Progress -Activity "Princess itineraries" -Completed

[pscustomobject]@{ cruises=$all } |
  ConvertTo-Json -Depth 20 -Compress |
  Set-Content ".\princess-itineraries.json" -Encoding UTF8


Write-Host ""
Write-Host "Princess acquisition complete."
Write-Host "  princess-products.json"
Write-Host "  princess-ports.json"
Write-Host "  princess-ships.json"
Write-Host "  princess-itineraries.json"
