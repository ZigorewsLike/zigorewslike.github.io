import { createStore } from 'redux'
import rootReducer from '../reducers/name'

export default function configureStore(initialState) {
  const store = createStore(rootReducer, initialState)

  if (module.hot) {
    module.hot.accept('../reducers', () => {
      const nextRootReducer = require('../reducers/name')
      store.replaceReducer(nextRootReducer)
    })
  }

  return store
}
