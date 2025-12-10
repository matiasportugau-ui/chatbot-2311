"use strict";(()=>{var e={};e.id=8630,e.ids=[8630],e.modules={20399:e=>{e.exports=require("next/dist/compiled/next-server/app-page.runtime.prod.js")},30517:e=>{e.exports=require("next/dist/compiled/next-server/app-route.runtime.prod.js")},84770:e=>{e.exports=require("crypto")},93647:(e,o,r)=>{r.r(o),r.d(o,{originalPathname:()=>P,patchFetch:()=>v,requestAsyncStorage:()=>h,routeModule:()=>b,serverHooks:()=>C,staticGenerationAsyncStorage:()=>y});var a={};r.r(a),r.d(a,{GET:()=>x,POST:()=>f,dynamic:()=>g});var s=r(49303),n=r(88716),t=r(60670),i=r(87070),c=r(68599),u=r(49604);let d={productos:c.rZ,buscarProducto:c.A3,obtenerEspesoresDisponibles:c.RI,obtenerPrecio:c.C8};function p(e){let o=e.toLowerCase(),r=[];for(let[e,a]of Object.entries(c.rZ))(o.includes(e)||o.includes(a.nombre.toLowerCase()))&&r.push({id:e,nombre:a.nombre,descripcion:a.descripcion,precios:a.precios});return r}class l{async procesarConsulta(e,o){try{let r=await (0,u.Cw)(e);switch(this.determinarTipoConsulta(e,r)){case"cotizacion":return await this.generarRespuestaCotizacion(r,o);case"informacion":return await this.generarRespuestaInformacion(e);case"pregunta":return await this.generarRespuestaPregunta(e);default:return this.generarRespuestaError(e)}}catch(o){return console.error("Error procesando consulta:",o),this.generarRespuestaError(e,o.message)}}determinarTipoConsulta(e,o){let r=e.toLowerCase();return["cotizar","precio","costo","cuanto","presupuesto","cotizaci\xf3n","isodec","isoroof","isopanel","isowall","chapa","calameria","panel","techo","pared","galp\xf3n","galpon","m2","metro"].some(e=>r.includes(e))?"cotizacion":["que es","como funciona","caracteristicas","especificaciones","diferencia","ventajas","beneficios","aplicaciones"].some(e=>r.includes(e))?"informacion":["como","cuando","donde","por que","que","cual","cuanto tiempo","garantia","instalacion","flete","entrega"].some(e=>r.includes(e))?"pregunta":o.producto?.tipo?"cotizacion":"pregunta"}async generarRespuestaCotizacion(e,o){this.detectarZonaPorTelefono(o);let r=function(e,o){try{let o=1,r=1;return e.dimensiones?.area_m2?(o=e.dimensiones.area_m2,r=1):e.dimensiones?.ancho&&e.dimensiones?.largo?(o=e.dimensiones.ancho,r=e.dimensiones.largo):e.dimensiones?.ancho&&(o=e.dimensiones.ancho,r=1),(0,c.L5)({producto:e.producto?.tipo||"isodec",dimensiones:{ancho:o,largo:r,espesor:e.producto?.grosor?parseInt(e.producto.grosor):100},servicios:e.servicios||[],cantidad:e.producto?.cantidad||1})}catch(e){throw Error("Error generando cotizaci\xf3n: "+(e instanceof Error?e.message:String(e)))}}(e,0);if(!r.producto)return{tipo:"error",mensaje:'No pude identificar el producto en tu consulta. \xbfPodr\xedas ser m\xe1s espec\xedfico? Por ejemplo: "Necesito cotizar Isodec 100mm para galp\xf3n de 50m2"',productos_sugeridos:this.obtenerProductosSugeridos(e.consulta_original||"")};let a=this.generarCodigoCotizacion(o),s=`🏗️ **COTIZACI\xd3N BMC** - C\xf3digo: ${a}

`;return s+=`📋 **${r.producto}**

💰 **Detalle de Precios:**
• \xc1rea: ${r.dimensiones}
• Precio unitario: $${r.precioUnitario?.toFixed(2)||"0"}/m\xb2
• Subtotal: $${r.subtotal?.toFixed(2)||"0"}
`,(e.servicios?.instalacion||e.servicios?.flete||e.servicios?.accesorios)&&(s+=`• Servicios adicionales incluidos
`),{tipo:"cotizacion",mensaje:s+=`
🎯 **TOTAL: $${r.precioFinal?.toFixed(2)||"0"}**

📞 **Pr\xf3ximos pasos:**
• Confirmar dimensiones exactas
• Coordinar visita t\xe9cnica (si es necesario)
• Definir fecha de entrega

\xbfTe interesa esta cotizaci\xf3n? \xa1Cont\xe1ctanos para m\xe1s detalles! 🚀`,cotizacion:{producto:r.producto,descripcion:r.dimensiones,precio_base:r.subtotal,servicios:{},total:r.precioFinal,recomendaciones:[],codigo:a},proximos_pasos:["Confirmar dimensiones exactas","Coordinar visita t\xe9cnica","Definir fecha de entrega","Firmar contrato"]}}async generarRespuestaInformacion(e){let o=p(e);if(0===o.length)return{tipo:"informacion",mensaje:`No encontr\xe9 informaci\xf3n espec\xedfica sobre "${e}". 

Te puedo ayudar con informaci\xf3n sobre nuestros productos principales:

🏗️ **Isodec EPS** - Paneles aislantes para paredes y techos
🏠 **Isoroof** - Paneles para techos con acabado met\xe1lico  
🏢 **Isopanel** - Paneles de uso general
🧱 **Isowall** - Paneles espec\xedficos para paredes exteriores
🔧 **Calamer\xeda** - Estructura met\xe1lica de soporte
📐 **Chapas** - Chapas galvanizadas

\xbfSobre cu\xe1l te gustar\xeda saber m\xe1s?`,productos_sugeridos:this.obtenerProductosSugeridos(e)};let r=o[0],a=`📋 **${r.nombre}**

`;for(let[e,o]of(a+=`${r.descripcion}

💰 **Precios disponibles:**
`,Object.entries(r.precios)))a+=`• ${e}: $${o}/m\xb2
`;return{tipo:"informacion",mensaje:a+=`
\xbfTe interesa cotizar este producto? \xa1Dime las dimensiones de tu proyecto! 📐`,productos_sugeridos:o.slice(1,4).map(e=>({nombre:e.nombre,descripcion:e.descripcion,precio_estimado:50,aplicaciones:[]}))}}async generarRespuestaPregunta(e){let o=this.obtenerPreguntasFrecuentes(e);return o.length>0?{tipo:"pregunta",mensaje:`🤔 **Pregunta Frecuente**

${o[0].respuesta}`,preguntas_frecuentes:o}:{tipo:"pregunta",mensaje:`Hola! 👋 

No estoy seguro de entender tu pregunta. Te puedo ayudar con:

📋 **Cotizaciones** - Dime qu\xe9 producto necesitas y las dimensiones
ℹ️ **Informaci\xf3n** - Sobre nuestros productos y servicios  
❓ **Preguntas** - Sobre instalaci\xf3n, flete, garant\xedas, etc.

\xbfEn qu\xe9 te puedo ayudar espec\xedficamente?`,preguntas_frecuentes:this.obtenerPreguntasFrecuentes("general")}}generarRespuestaError(e,o){return{tipo:"error",mensaje:`Lo siento, hubo un problema procesando tu consulta. 😔

${o?`Error: ${o}`:"Por favor, intenta reformular tu pregunta."}

Puedes contactarnos directamente al 📞 [tel\xe9fono] o escribirnos de nuevo con m\xe1s detalles.`}}detectarZonaPorTelefono(e){return e&&({2:"montevideo",4:"canelones",5:"fray_bentos",6:"colonia"})[e.slice(0,1)]||"montevideo"}generarCodigoCotizacion(e){let o=Date.now().toString().slice(-6),r=e?e.slice(-3):"000";return`BMC${o}${r}`}obtenerProductosSugeridos(e){return p(e).slice(0,3).map(e=>({nombre:e.nombre,descripcion:e.descripcion,precio_estimado:50,aplicaciones:[]}))}obtenerPreguntasFrecuentes(e){let o=e.toLowerCase();return[{pregunta:"\xbfCu\xe1nto tiempo tarda la entrega?",respuesta:"La entrega depende de la zona y disponibilidad. En Montevideo: 3-5 d\xedas h\xe1biles. Interior: 5-10 d\xedas h\xe1biles. Te confirmamos el plazo exacto al confirmar la cotizaci\xf3n."},{pregunta:"\xbfIncluyen instalaci\xf3n?",respuesta:"S\xed, ofrecemos servicio de instalaci\xf3n profesional. El costo se calcula seg\xfan la complejidad y \xe1rea del proyecto. Incluye mano de obra especializada y garant\xeda de instalaci\xf3n."},{pregunta:"\xbfQu\xe9 garant\xeda tienen los productos?",respuesta:"Nuestros productos tienen garant\xeda de 10 a\xf1os contra defectos de fabricaci\xf3n. La instalaci\xf3n tiene garant\xeda de 2 a\xf1os. Todos los productos cumplen normas IRAM y certificaciones internacionales."},{pregunta:"\xbfHacen flete a todo el pa\xeds?",respuesta:"S\xed, realizamos flete a todo Uruguay. El costo var\xeda seg\xfan la zona y peso del material. En Montevideo y Canelones el flete es m\xe1s econ\xf3mico. Te calculamos el costo exacto seg\xfan tu ubicaci\xf3n."},{pregunta:"\xbfQu\xe9 formas de pago aceptan?",respuesta:"Aceptamos efectivo, transferencia bancaria, tarjeta de cr\xe9dito y d\xe9bito. Para proyectos grandes ofrecemos financiaci\xf3n a trav\xe9s de bancos conveniados. Consulta por planes de pago especiales."}].filter(e=>e.pregunta.toLowerCase().includes(o)||e.respuesta.toLowerCase().includes(o))}constructor(){this.knowledgeBase=d}}let m=new l,g="force-dynamic";async function f(e){try{let{consulta:o,telefono:r,includeMetadata:a=!1}=await e.json();if(!o||"string"!=typeof o)return i.NextResponse.json({success:!1,error:"consulta is required and must be a string"},{status:400});let s=await m.procesarConsulta(o,r),n={success:!0,data:s,...a&&{metadata:{timestamp:new Date().toISOString(),consulta_original:o,telefono:r||null,procesado_por:"quote-engine-v1.0"}}};return i.NextResponse.json(n)}catch(e){return console.error("Error in quote-engine API:",e),i.NextResponse.json({success:!1,error:e instanceof Error?e.message:"Unknown error",data:{tipo:"error",mensaje:"Error interno del sistema. Por favor, intenta de nuevo."}},{status:500})}}async function x(e){try{let{searchParams:o}=new URL(e.url),r=o.get("q"),a=o.get("tipo")||"all";if(!r)return i.NextResponse.json({success:!1,error:"query parameter is required"},{status:400});let s=await m.procesarConsulta(r);return i.NextResponse.json({success:!0,data:s,query:r,tipo:a})}catch(e){return console.error("Error in quote-engine GET:",e),i.NextResponse.json({success:!1,error:e instanceof Error?e.message:"Unknown error"},{status:500})}}let b=new s.AppRouteRouteModule({definition:{kind:n.x.APP_ROUTE,page:"/api/quote-engine/route",pathname:"/api/quote-engine",filename:"route",bundlePath:"app/api/quote-engine/route"},resolvedPagePath:"/Users/matias/chatbot-2311/src/app/api/quote-engine/route.ts",nextConfigOutput:"standalone",userland:a}),{requestAsyncStorage:h,staticGenerationAsyncStorage:y,serverHooks:C}=b,P="/api/quote-engine/route";function v(){return(0,t.patchFetch)({serverHooks:C,staticGenerationAsyncStorage:y})}}};var o=require("../../../webpack-runtime.js");o.C(e);var r=e=>o(o.s=e),a=o.X(0,[8948,5972,1088,9604,8599],()=>r(93647));module.exports=a})();