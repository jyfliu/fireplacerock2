
export function unserializeTemplate(template) {
  if (!template) {
    return template;
  }
  if (template.sprite) {
    let spriteImg = new Image();
    spriteImg.src = `data:image/jpg;base64,${template.sprite}`;
    template.spriteImg = spriteImg
    template.is_mini = false
  }

  if (template.mini_sprite) {
    let spriteImg = new Image();
    spriteImg.src = `data:image/jpg;base64,${template.mini_sprite}`;
    template.spriteImg = spriteImg
    template.isMini = true
  }

  return template;
}