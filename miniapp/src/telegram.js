export function initTelegram() {
 const tg = window.Telegram?.WebApp;
 if (!tg) {
   return {
     isAvailable: false,
     user: null,
     initData: "",
     chat: null
   };
 }
 tg.ready();
 tg.expand();
 return {
   isAvailable: true,
   user: tg.initDataUnsafe?.user || null,
   initData: tg.initData || "",
   chat: tg.initDataUnsafe?.chat || null,
   theme: tg.colorScheme || "light"
 };
}
