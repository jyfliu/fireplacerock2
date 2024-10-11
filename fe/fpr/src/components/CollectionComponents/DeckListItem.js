


export default function DeckListItem(props) {
  const { card, count, removeFromDeck } = props

  console.log('deck list item', count, card)
  console.log('name', card.name)
  console.log('count', count)



  return <div>
    test
    <h4>{card.name}</h4>
    <h4>{count}</h4>
  </div>;
}