<script>
    export let card = "as";
    card = card.toLowerCase();
  
    // Construct the path to the card image
    const cardImage = `/deck/${card}.svg`;
  </script>
  
  <div class="card">
    <img src={cardImage} alt={`Card ${card}`} />
  </div>
  
  <style>
    img {
      filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.2));
      width: 100px; /* Scale SVGs to fit card size */
      height: auto;
    }
  </style>