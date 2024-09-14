
// terrible code I found online that log mixes the colour c with white
// based on the percentage p
// example: pSBC(0.4, "rgb(12,30,45)")
export function pSBC(pct,C) {
    var i=parseInt,r=Math.round,[a,b,c,d]=C.split(","),P2=pct<0,t=P2?0:pct*255**2,P=P2?1+pct:1-pct;
    return"rgb"+(d?"a(":"(")+r((P*i(a[3]==="a"?a.slice(5):a.slice(4))**2+t)**0.5)+","+r((P*i(b)**2+t)**0.5)+","+r((P*i(c)**2+t)**0.5)+(d?","+d:")");
}

export function vh(percent) {
  var h = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
  return (percent * h) / 100;
}

export function vw(percent) {
  var w = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
  return (percent * w) / 100;
}

export function vmin(percent) {
  return Math.min(vh(percent), vw(percent));
}

export function inches(num) {
  return window.devicePixelRatio * 96 * num;
}
