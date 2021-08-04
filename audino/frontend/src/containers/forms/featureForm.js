
import React from 'react';
import axios from 'axios';
import { withRouter } from 'react-router';
import { withStore } from '@spyna/react-store';

import Alert from '../../components/alert';
import FeatureChecklist from '../../components/checklist';

class FeatureForm extends React.Component {
  constructor(props) {
    super(props);

    this.initialState = {
      projectId: props.projectId,
      errorMessage: '',
      successMessage: '',
      featuresEnabled: {
        'next button': true,
        '2D Labels': false,
        'playbackOn': false,
        'example 3': false
      }
    };

    this.state = { ...this.initialState };
  }

  componentDidMount() {
    const { projectId } = this.state;
    const { featuresEnabled } = this.state;
    axios({
      method: 'get',
      url: `api/projects/${projectId}/toggled`
    })
      .then(response => {
        // take all the current values of featuresList, include the new ones defined at the line 27
        const featuresList = response.data.features_list;
        if (!featuresList) {
          return;
        }
        Object.entries(featuresList).forEach(([key, value]) => {
          featuresEnabled[key] = value;
        });
        this.setState({
          featuresEnabled
        });
      })
      .catch(error => {
        console.error(error)
        this.setState({
          errorMessage: error.response.data.message
        });
      });
  }

  handleSubmitFeatures(e) {
    e.preventDefault();
    const { featuresEnabled, projectId } = this.state;
    axios({
      method: 'patch',
      url: '/api/projects/toggled',
      data: {
        featuresEnabled,
        projectId
      }
    })
      .then(response => {
        this.setState({
          successMessage: 'successfully updated features'
        });
      })
      .catch(error => {
        this.setState({
          successMessage: '',
          errorMessage: error.response.data.message
        });
      });
  }

  handleCheck(value) {
    const { featuresEnabled } = this.state;
    featuresEnabled[value] = !featuresEnabled[value];
    this.setState({
      featuresEnabled
    });
  }

  renderFeatureCols(start, end, feature_list) {
    const { errorMessage,  successMessage} = this.state;
    return (
      <div>
        <form
          style={{
            float: 'left',
            width: '25%'
          }}
        >
          {errorMessage ? <Alert type="danger" message={errorMessage} /> : null}
          {successMessage ? <Alert type="success" message={successMessage} /> : null}
          {feature_list.slice(start, end).map(([key, value]) => {
            return (
              <FeatureChecklist
                item={key}
                isChecked={value}
                handleCheck={() => {
                  this.handleCheck(key);
                }}
              />
            );
          })}
        </form>
      </div>
    );
  }

  render() {
    const { featuresEnabled } = this.state;
    const feature_list = Object.entries(featuresEnabled);
    const numPerCol = feature_list.length / 4;
    return (
      <div>
        <div style={{ display: 'table', justifyContent: 'space-evenly', width: '100%' }}>
          {this.renderFeatureCols(0, numPerCol, feature_list)}
          {this.renderFeatureCols(numPerCol * 1, numPerCol * 2, feature_list)}
          {this.renderFeatureCols(numPerCol * 2, numPerCol * 3, feature_list)}
          {this.renderFeatureCols(numPerCol * 3, feature_list.length, feature_list)}
        </div>
        <input
          style={{ position: 'relative', width: '10%', left: '45%' }}
          type="submit"
          value="Submit"
          onClick={e => this.handleSubmitFeatures(e)}
        />
      </div>
    );
  }
}

export default withStore(withRouter(FeatureForm));