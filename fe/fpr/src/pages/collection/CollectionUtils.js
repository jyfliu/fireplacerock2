
export function unserializeTemplate(template) {
  if (!template) {
    return template;
  }
  if (template.sprite) {
    let sprite_img = new Image();
    sprite_img.src = `data:image/jpg;base64,${template.sprite}`;
    template.sprite_img = sprite_img
  }

  if (template.mini_sprite) {
    let sprite_img = new Image();
    sprite_img.src = `data:image/jpg;base64,${template.mini_sprite}`;
    template.sprite_img = sprite_img
  }

  return template;
}