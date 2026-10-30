const HB = 'https://www.hollandandbarrett.com';
export function supplementProducts(profile = {}, answers = {}, now = new Date()) {
  const vegan = profile.supplement_diet === 'Vegan';
  const plantDiet = ['Vegan', 'Vegetarian'].includes(profile.supplement_diet);
  const winter = now.getMonth() >= 9 || now.getMonth() <= 2;
  const lowSun = profile.sun_exposure === 'Limited' || ['Care home', 'Assisted living'].includes(profile.living_arrangement);
  const memory = ['forgetting', 'confused_day_place', 'memory_concern_other'].some(key => answers[key] === 'Yes');
  const vision = answers.vision_problem === 'Yes';
  const focus = profile.shopping_focus || 'All products';
  const products = [
    { id:'vitd', category:'Everyday nutrition', title:vegan ? 'Vegan vitamin D options' : 'H&B Vitamin D · 10µg (400 IU)', tag:lowSun ? 'Limited sunlight' : winter ? 'Seasonal consideration' : 'Everyday nutrition', matched:winter || lowSun,
      why:lowSun ? 'Your profile suggests limited sunlight. NHS guidance recommends considering vitamin D throughout the year for people with little sun exposure.' : winter ? 'It is autumn or winter in the UK. NHS guidance says adults should consider a daily 10µg vitamin D supplement in these months.' : 'Browse vitamin D options. With regular sunlight, a supplement may not be needed during spring and summer.',
      check:'Check existing supplements to avoid doubling up. Ask a pharmacist about suitability and follow the label. Check the source of vitamin D if you are vegan.',
      evidence:'UK seasonal guidance', source:'https://www.nhs.uk/conditions/vitamins-and-minerals/vitamin-d/',
      url:vegan ? `${HB}/shop/vitamins-supplements/vitamins/vitamin-d/?t=is_suitable_for%3Avegan` : `${HB}/shop/product/holland-barrett-vitamin-d-400-i-u-10ug-240-tablets-6100024812` },
    { id:'b12',category:'Everyday nutrition',title:'Vitamin B12 · Vegan options',tag:plantDiet ? 'Your eating pattern' : 'Vegan & vegetarian diets',matched:plantDiet,
      why:plantDiet ? `You selected a ${profile.supplement_diet.toLowerCase()} diet. Review B12 from fortified foods and other sources; a supplement may help if intake is inadequate.` : 'Explore B12 products suitable for vegan diets. Select your eating pattern above to personalise this option; your assessment does not establish a deficiency.',
      check:'A pharmacist can help choose a formulation. Symptoms or suspected deficiency need assessment; do not assume tiredness or memory changes mean low B12.',
      evidence:'Diet-dependent nutritional need',source:'https://www.nhs.uk/live-well/eat-well/how-to-eat-a-balanced-diet/the-vegan-diet/',
      url:`${HB}/shop/vitamins-supplements/vitamins/vitamin-b/vitamin-b12/?t=is_suitable_for%3Avegan` },
    { id:'coq10',category:'Heart health',title:'CoQ10 · Coenzyme Q10',tag:'Heart health interest',matched:focus === 'Heart health',
      why:focus === 'Heart health' ? 'You chose to explore heart health products. CoQ10 is often marketed in this area; your wellness scores do not show that you need it.' : 'Browse CoQ10 products commonly marketed for heart health. No heart condition or need for CoQ10 is inferred from your assessment.',
      check:'Evidence for heart benefits is inconclusive. CoQ10 can interact with warfarin and insulin. Check with a pharmacist or clinician, especially if taking heart medicines; it does not replace treatment.',
      evidence:'Benefits uncertain · interaction check',source:'https://www.nccih.nih.gov/health/coenzyme-q10',
      url:`${HB}/shop/vitamins-supplements/supplements/co-enzyme-q10/` },
    { id:'lionsmane',category:'Memory & focus',title:'Lion’s Mane · Mushroom supplements',tag:memory ? 'Memory concern reported' : 'Memory & focus interest',matched:memory || focus === 'Memory & focus',
      why:memory ? 'You reported a memory or thinking concern. Lion’s Mane is shown as a product to learn about, alongside a reminder to discuss the concern with your GP.' : 'Explore Lion’s Mane products marketed for focus and cognitive wellbeing. This is a browsing option, not a recommendation to treat a memory problem.',
      check:'Research is early and evidence is limited. These products are not established treatments for memory loss or dementia. Check mushroom allergies and medicines; new or worsening memory changes need a GP review.',
      evidence:'Early research · limited evidence',source:'https://www.hollandandbarrett.com/shop/vitamins-supplements/supplements/plant-sourced-supplements/functional-mushrooms/?t=main_ingredient%3Alion-s-mane-mushroom',
      url:`${HB}/shop/category/lions-mane/` },
    { id:'lutein',category:'Vision',title:'Lutein · Eye nutrition options',tag:vision ? 'Vision concern reported' : 'Eye nutrition interest',matched:vision || focus === 'Vision',
      why:vision ? 'You reported a vision problem. Browse lutein products to discuss with your optometrist; that answer alone cannot establish whether an eye supplement is appropriate.' : 'Explore lutein and eye-nutrition formulas. Your profile has not established a need for a vision supplement.',
      check:'Benefits of AREDS2 formulas apply to specific diagnosed stages of age-related macular degeneration, not all vision problems. Lutein alone or another eye blend is not automatically equivalent. Ask your eye-care professional.',
      evidence:'Condition-specific evidence · eye review',source:'https://www.nei.nih.gov/eye-health-information/eye-conditions-and-diseases/age-related-macular-degeneration/nutritional-supplements-age-related-macular-degeneration',
      url:`${HB}/shop/vitamins-supplements/supplements/plant-sourced-supplements/lutein/` },
    { id:'bilberry',category:'Vision',title:'Bilberry extract + Lutein · ClearVision',tag:'Eye nutrition blend',matched:vision || focus === 'Vision',
      why:vision ? 'You reported a vision concern. This H&B-listed Supplement Place blend contains bilberry, lutein, zeaxanthin and pine bark; it is an option to discuss, not a treatment selected for your symptoms.' : 'Compare this bilberry-containing blend listed at H&B. Sold by Supplement Place; check the current seller and label before purchase.',
      check:'Bilberry has not been clearly shown to improve eye conditions. This blend is not presented as an AREDS2 formula. Check medicines and overlapping ingredients with a pharmacist; do not delay an eye examination.',
      evidence:'Bilberry benefits not established',source:'https://www.nccih.nih.gov/health/bilberry',
      url:`${HB}/shop/product/supplement-place-clearvision-pine-bark-bilberry-lutein-zeaxanthin-60-capsules-6100024986` },
  ];
  return products.filter(item => focus === 'All products' || item.category === focus).sort((a,b) => Number(b.matched) - Number(a.matched)).map(item => ({...item,link:'View at Holland & Barrett'}));
}
