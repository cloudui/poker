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
    .card {
      width: 100px; /* Adjust as needed */
      height: 140px; /* Adjust as needed */
      display: flex;
      justify-content: center;
      align-items: center;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      border-radius: 3px;
      background-color: white;
    }
  
    img {
      width: 100%; /* Scale SVGs to fit card size */
      height: auto;
    }
  </style>