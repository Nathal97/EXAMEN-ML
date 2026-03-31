
import { useState } from 'react';
import './Game.css'

function Game() {
  const [AllCases, setAllCases] = useState(Array(9).fill(null))
  const [user, setUser] = useState(1);

  // X = 1 et O = -1
  const handleClick = (index) => {
    const newCases = [...AllCases]
    if (newCases[index] == null) {
      newCases[index] = user
      setUser(-1 * user)
      setAllCases([...newCases])
    }
  } 

  return (
    <div className='AllScreen'>
      <text>MORPION</text>
      <div>
        <text>Player</text>
        <div className='playerIntro'>
          <div className='playerCase'><div className='userX'></div></div>
          <text>VS</text>
          <div className='playerCase'><div className='userCircle'></div></div>
        </div>
      </div>

      <section id="gameContainer">
        {/* GAME */}
        {
          AllCases.map((value, index)=>(
            <div key={index} className='case' onClick={()=>handleClick(index)}>
              <div className={`${value==1? "userX" : value == -1?"userCircle":""}`}>

              </div>
            </div>
          ))
        }
      </section>
    </div>
  )
}

export default Game
